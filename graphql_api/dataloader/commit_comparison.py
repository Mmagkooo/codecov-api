import functools
import operator

from aiodataloader import DataLoader
from asgiref.sync import sync_to_async
from django.db.models import Prefetch, Q

from compare.models import CommitComparison
from core.models import Commit
from reports.models import CommitReport


class CommitComparisonLoader(DataLoader):
    @sync_to_async
    def batch_load_fn(self, keys):
        # TODO: can we generate SQL like "WHERE (base_commitid, compare_commitid) IN ((1, 2), (3, 4))"" instead?
        filter = functools.reduce(
            operator.or_,
            [
                Q(base_commit__commitid=base_id, compare_commit__commitid=compare_id)
                for base_id, compare_id in keys
            ],
        )

        commit_queryset = Commit.objects.prefetch_related(
            Prefetch(
                "reports",
                queryset=CommitReport.objects.select_related("reportleveltotals"),
            )
        )
        queryset = CommitComparison.objects.filter(filter).prefetch_related(
            Prefetch("base_commit", queryset=commit_queryset),
            Prefetch("compare_commit", queryset=commit_queryset),
        )

        results = {
            (
                commit_comparison.base_commit.commitid,
                commit_comparison.compare_commit.commitid,
            ): commit_comparison
            for commit_comparison in queryset
        }

        # the returned list of comparisons must be in the exact order of `keys`
        return [results.get(key) for key in keys]


def commit_comparison_loader(info):
    CONTEXT_KEY = f"__comparison_loader"
    if CONTEXT_KEY not in info.context:
        # One loader per HTTP request that we init when we need it
        info.context[CONTEXT_KEY] = CommitComparisonLoader()
    return info.context[CONTEXT_KEY]


def load_commit_comparison(info, key):
    return commit_comparison_loader(info).load(key)


def cache_commit_comparison(info, commit_comparison):
    key = (
        commit_comparison.base_commit.commitid,
        commit_comparison.compare_commit.commitid,
    )
    loader = commit_comparison_loader(info)
    loader.prime(key, commit_comparison)
