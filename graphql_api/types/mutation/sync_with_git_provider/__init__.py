from graphql_api.helpers.ariadne import ariadne_load_local_graphql

from .sync_with_git_provider import (
    resolve_sync_with_git_provider,
    error_sync_with_git_provider,
)


gql_sync_with_git_provider = ariadne_load_local_graphql(
    __file__, "sync_with_git_provider.graphql"
)
