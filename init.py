#!/usr/bin/python3

from redminelib import Redmine
import settings


class RedmineBackport:
    def __init__(self, url, key):
        self.redmine = Redmine(url, key=key)

    def _get_user_id(self):
        user = self.redmine.user.get(settings.USER_NAME)
        return user.id

    def _get_version(self):
        versions = self.redmine.version.filter(
            project_id=settings.PROJECT_NAME)
        latest = filter(lambda v: v.name == settings.PROJECT_VERSION, versions)
        latest = list(latest)[0].id
        return latest

    def print_bp_candidates(self):
        user_id = self._get_user_id()
        version_id = self._get_version()
        issues = self.redmine.issue.filter(project_id=settings.PROJECT_NAME,
                                           assigned_to_id=user_id,
                                           fixed_version_id=version_id,
                                           include="relations",
                                           is_private=settings.PRIVATE,)
        if settings.PRIVATE:
            input(
                "You are proceeding with backports for PRIVATE tickets, do you wish to continue?")
        for issue in issues:
            copied_from = [(rel.issue_id, rel.issue_to_id)
                           for rel in issue.relations if rel.relation_type == "copied_to"]
            for issue, bp_issue in copied_from:
                cur_issue = self.redmine.issue.filter(issue_id=issue)
                if not cur_issue:
                    print("Possible backport candidate: ", bp_issue)


def main():
    key = settings.REDMINE_KEY
    if key:
        rm_bp = RedmineBackport(settings.REDMINE_URL, key)
        rm_bp.print_bp_candidates()
    else:
        print("Key ERROR!")
        sys.exit(1)
    return 0


if __name__ == "__main__":
    main()
