#!/usr/bin/python3

from redminelib import Redmine
import settings


def get_user_id(redmine):
    user = redmine.user.get(settings.USER_NAME)
    return user.id

def get_version(redmine):
    versions = redmine.version.filter(project_id=settings.PROJECT_NAME)
    latest = filter(lambda v: v.name == settings.PROJECT_VERSION, versions)
    latest = list(latest)[0].id
    return latest

def print_bp_candidates(redmine):
    projects = redmine.project.all()
    user_id = get_user_id(redmine)
    version_id = get_version(redmine)
    issues = redmine.issue.filter(project_id=settings.PROJECT_NAME,
            assigned_to_id=user_id,
            fixed_version_id=version_id,
            include="relations",
            is_private=settings.PRIVATE,)
    for issue in issues:
        copied_from = [(rel.issue_id, rel.issue_to_id) for rel in issue.relations if rel.relation_type == "copied_to"]
        for issue, bp_issue in copied_from:
            cur_issue = redmine.issue.filter(issue_id=issue)
            if not cur_issue:
                print("Possible backport candidate: ", bp_issue)

def main():
    key = settings.REDMINE_KEY
    if key:
        redmine = Redmine(settings.REDMINE_URL, key=key)
        print_bp_candidates(redmine)
    else:
        print("Key ERROR!")
        sys.exit(1)
    return 0

if __name__ == "__main__":
    main()
