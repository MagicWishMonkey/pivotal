from fusion import tools
from .containers import *


class Tracker(object):
    __default_project_id__ = None

    def __init__(self, token, database):
        PivotalObject.__token__ = token

        if isinstance(database, basestring) is True:
            database = tools.file(database)


        self.database = database
        self.__object__ = {}
        self.__status__ = {}
        self.__stories__ = []
        self.__projects__ = []
        self.__accounts__ = []

        #database.delete()
        if database.exists is False:
            database.write_text(tools.json({"projects": [], "accounts": [], "stories": [], "status": {}}))
            self.sync()
        else:
            self.load()


    def load(self):
        data = self.database.read_text()
        object = tools.unjson(data)
        self.__object__ = object

        self.__status__ = object["status"]

        projects = object["projects"]
        projects = Project.spawn(projects)
        self.__projects__ = projects

        stories = object["stories"]
        stories = Story.spawn(stories)
        self.__stories__ = stories

        accounts = object["accounts"]
        accounts = Account.spawn(accounts)
        self.__accounts__ = accounts

    def save(self):
        obj = {}
        obj["status"] = self.__status__

        projects = self.projects
        projects = [o.deflate() for o in projects]
        obj["projects"] = projects

        stories = self.stories
        stories = [o.deflate() for o in stories]
        obj["stories"] = stories


        accounts = self.accounts
        accounts = [o.deflate() for o in accounts]
        obj["accounts"] = accounts

        data = tools.json(obj)
        self.database.write_text(data)

    def bind(self, project=None, story=None, account=None):
        if project is not None:
            self.current_project_id = project
        if story is not None:
            self.current_story_id = story
        if account is not None:
            self.current_account_id = account
        return self

    @property
    def projects(self):
        return self.__projects__

    @projects.setter
    def projects(self, lst):
        self.__projects__ = lst
        self.__object__["projects"] = lst

    @property
    def stories(self):
        return self.__stories__

    @stories.setter
    def stories(self, lst):
        self.__stories__ = lst
        self.__object__["stories"] = lst

    @property
    def accounts(self):
        return self.__accounts__

    @accounts.setter
    def accounts(self, lst):
        self.__accounts__ = lst
        self.__object__["accounts"] = lst


    @property
    def current_project(self):
        id = self.current_project_id
        if id is None:
            return None
        return self.project(id)

    @property
    def current_project_id(self):
        try:
            return self.__status__["project_id"]
        except:
            return None

    @current_project_id.setter
    def current_project_id(self, key):
        project = key if isinstance(key, Project) is True else self.project(key)
        project_id = project.id
        try:
            if self.__status__["project_id"] == project_id:
                return
            self.__status__["story_id"] = None
        except:
            pass

        self.__status__["project_id"] = project_id
        self.save()

    @property
    def current_story(self):
        id = self.current_story_id
        if id is None:
            return None
        return self.story(id)

    @property
    def current_story_id(self):
        try:
            return self.__status__["story_id"]
        except:
            return None

    @current_story_id.setter
    def current_story_id(self, key):
        story = key if isinstance(key, Story) is True else self.story(key)
        story_id = story.id
        try:
            if self.__status__["story_id"] == story_id:
                return
        except:
            pass

        self.__status__["story_id"] = story_id
        self.__status__["project_id"] = story.project_id
        self.save()

    @property
    def current_account(self):
        id = self.current_account_id
        if id is None:
            return None
        return self.account(id)

    @property
    def current_account_id(self):
        try:
            return self.__status__["account_id"]
        except:
            return None

    @current_account_id.setter
    def current_account_id(self, key):
        account = key if isinstance(key, Account) is True else self.account(key)
        account_id = account.id
        try:
            if self.__status__["account_id"] == account_id:
                return
        except:
            pass

        self.__status__["account_id"] = account_id
        self.save()

    def update_projects(self):
        projects = Project.export()
        current_projects = self.projects

        modified = False
        keychain = set([p.id for p in projects])
        removed = [p for p in current_projects if p.id not in keychain]
        if len(removed) > 0:
            modified = True
        elif len(projects) != len(current_projects):
            modified = True

        if modified is True:
            current_stories = self.stories
            stories = current_stories
            stories = [o for o in stories if o.project_id not in keychain]
            self.projects = projects
            self.stories = stories
            self.save()

    def update_stories(self):
        projects = self.projects
        stories = []
        for project in projects:
            lst = project.stories
            if len(lst) > 0:
                stories.extend(lst)

        self.stories = stories
        self.save()

    def update_accounts(self):
        projects = self.projects
        accounts = []
        for project in projects:
            lst = project.accounts
            if len(lst) > 0:
                accounts.extend(lst)

        accounts = dict((o.email, o) for o in accounts)
        accounts = accounts.values()
        self.accounts = accounts
        self.save()

    def sync(self):
        self.update_projects()
        self.update_stories()
        self.update_accounts()
        self.load()

    def project(self, key):
        projects = self.projects
        name = str(key).strip().lower()
        if len(projects) == 0:
            self.update_projects()
            projects = self.projects
            lst = [p for p in projects if p.name.lower() == name or p.id == key]
            return lst[0] if len(lst) > 0 else None

        lst = [p for p in projects if p.name.lower() == name or p.id == key]
        if len(lst) == 0:
            self.update_projects()
            projects = self.projects
            lst = [p for p in projects if p.name.lower() == name or p.id == key]
        return lst[0] if len(lst) > 0 else None

    def story(self, key):
        stories = self.stories
        if len(stories) == 0:
            self.update_stories()
            stories = self.stories
            lst = [s for s in stories if s.name == key or s.id == key]
            return lst[0] if len(lst) > 0 else None

        lst = [s for s in stories if s.name == key or s.id == key]
        if len(lst) == 0:
            self.update_stories()
            stories = self.stories
            lst = [s for s in stories if s.name == key or s.id == key]
        return lst[0] if len(lst) > 0 else None

    def account(self, key):
        accounts = self.accounts
        if len(accounts) == 0:
            self.update_accounts()
            accounts = self.accounts
            lst = [a for a in accounts if a.is_match(key)]
            return lst[0] if len(lst) > 0 else None

        lst = [a for a in accounts if a.is_match(key)]
        if len(lst) == 0:
            self.update_accounts()
            accounts = self.accounts
            lst = [a for a in accounts if a.is_match(key)]
        return lst[0] if len(lst) > 0 else None

    def add_feature(self, label, description=None, owner=None, estimate=None):
        return self.add_story(
            label,
            description=description,
            owner=owner,
            estimate=estimate,
            type="Feature"
        )

    def add_chore(self, label, description=None, owner=None, estimate=None):
        return self.add_story(
            label,
            description=description,
            owner=owner,
            estimate=estimate,
            type="Chore"
        )

    def add_bug(self, label, description=None, owner=None, estimate=None):
        return self.add_story(
            label,
            description=description,
            owner=owner,
            estimate=estimate,
            type="Bug"
        )

    def add_story(self, label, description=None, owner=None, estimate=None, type="Feature"):
        account = self.current_account
        project = self.current_project
        if account is None:
            raise Exception("The active account is not assigned.")

        if project is None:
            raise Exception("The active project is not assigned.")

        type = type.strip().lower()
        if type not in ["feature", "bug", "chore", "release"]:
            type = "feature"

        if isinstance(estimate, int) is True:
            estimate = float(estimate)

        if owner is not None:
            owner = self.account(owner)

        story = project.add_story(
            account=account,
            owner=owner,
            type=type,
            label=label,
            description=description,
            estimate=estimate
        )
        stories = self.stories
        stories.append(story)
        self.save()
        return self




