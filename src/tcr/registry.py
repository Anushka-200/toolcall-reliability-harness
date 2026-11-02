from dataclasses import dataclass, field

@dataclass(frozen=True)
class Tool:
    name: str
    required: dict            # arg name -> python type
    access: str = "read"      # read | write
    needs_approval: bool = False
    optional: dict = field(default_factory=dict)

REGISTRY = {t.name: t for t in [
    Tool("gmail.search", {"query": str}, "read", optional={"max_results": int}),
    Tool("gmail.send", {"to": str, "subject": str, "body": str}, "write", needs_approval=True),
    Tool("crm.update_deal", {"deal_id": str, "stage": str}, "write", needs_approval=True),
    Tool("calendar.list", {"day": str}, "read"),
    Tool("slack.post", {"channel": str, "text": str}, "write", needs_approval=False),
]}
