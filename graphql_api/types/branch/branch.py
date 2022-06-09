from ariadne import ObjectType

branch_bindable = ObjectType("Branch")

@branch_bindable.field("head")
def resolve_head_commit(branch, info):
    command = info.context["executor"].get_command("commit")
    return command.fetch_commit(branch.repository, branch.head)
