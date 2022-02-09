#!/usr/bin/python3

from redminelib import Redmine
import settings
import toml


def load_conf():
    data = toml.load("config.toml")
    return data


class RedmineBackport:
    def __init__(self, url, key, latest_version, project):
        self.redmine = Redmine(url, key=key)
        self.project = project
        self.user_id = self._get_user_id()
        self.latest_version_id = self._get_version_id(latest_version)

    def _get_user_id(self):
        user = self.redmine.user.get(settings.USER_NAME)
        return user.id

    def _get_version_id(self, version):
        versions = self.redmine.version.filter(
            project_id=self.project)
        latest = filter(lambda v: v.name == version, versions)
        latest = list(latest)[0].id
        return latest

    def print_bp_candidates(self, version, private):
        version_id = self._get_version_id(version)
        issues = self.redmine.issue.filter(project_id=self.project,
#                                           assigned_to_id=self.user_id,
                                           fixed_version_id=version_id,
                                           include="relations",
                                           is_private=private,)
        if private:
            input(
                "You are proceeding with backports for PRIVATE tickets, do you wish to continue?")
        print("Ready to backport for {}:".format(version))
        i = 0
        for issue in issues:
            copied_to = [(rel.issue_id, rel.issue_to_id)
                         for rel in issue.relations if rel.relation_type == "copied_to"]
            for issue, bp_issue in copied_to:
                cur_issue = self.redmine.issue.filter(issue_id=issue)
                if not cur_issue:
                    i += 1
                    print("{}. {}/issues/{}".format(i,
                          settings.REDMINE_URL, str(bp_issue)))
        print("")

    def get_missing_tickets(self, version, label):
        issues = self.redmine.issue.filter(project_id=self.project,
                                           fixed_version_id=self.latest_version_id,
                                           include="relations",
                                           status_id="!rejected",
                                           cf_5=label,)
        unwanted_rel_types = ["relates", "duplicates", "duplicated",
                              "blocks", "blocked", "precedes", "follows", "copied_from"]
        print("Issues possibly missing backport tickets for {}:".format(version))
        i = 0
        for issue in issues:
#            print("ID: ", issue.id, list(issue.relations))
            if issue.relations:
                copied_to = [(rel.issue_id, rel.issue_to_id)
                             for rel in issue.relations if rel.relation_type == "copied_to"]
                if copied_to:
#                    print("copied_to: ", copied_to)
#                    import ipdb
#                    ipdb.set_trace()
                    version_id = self._get_version_id(version)
                    cur_issue = list()
                    for _, bp_issue in copied_to:
                        cur_issue.append(self.redmine.issue.filter(
                                fixed_version_id=version_id,
                                issue_id=bp_issue,
                                ))
                        #print("cur issue: ", list(cur_issue))
                    if cur_issue:
                        #print("Continuing")
                        continue
            i += 1
            print("{}. {}/issues/{}".format(i, settings.REDMINE_URL, str(issue.id)))

        print("")


def main():
    key = settings.REDMINE_KEY
    if key:
        conf = load_conf()
        rm_bp = RedmineBackport(
            settings.REDMINE_URL, key, conf["default"]["latest"], conf["default"]["project"])
        for k, v in conf.items():
            if k == "default":
                continue
            rm_bp.get_missing_tickets(conf[k]["version"], conf[k]["label"])
            rm_bp.print_bp_candidates(conf[k]["version"], conf[k]["private"])
    else:
        print("Key ERROR!")
        sys.exit(1)
    return 0


if __name__ == "__main__":
    main()
