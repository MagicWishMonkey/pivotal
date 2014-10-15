from fusion import tools



class PivotalObject(object):
    __token__ = None

    def __init__(self, **kwd):
        for key in kwd:
            val = kwd[key]
            self.__dict__[key] = val

    @property
    def token(self):
        return PivotalObject.__token__

    # @property
    # def tracker(self):
    #     return self.__tracker__

    @property
    def label(self):
        return self.__dict__["name"]

    @staticmethod
    def get(uri, fn=None):
        token = PivotalObject.__token__
        object = tools.http_get(uri, ("X-TrackerToken", token))
        if isinstance(object, basestring) is True:
            object = tools.unjson(object)

        if isinstance(object, list) is True:
            objects = [ServerObject.create(**(o)) for o in object]
            if fn is not None:
                objects = fn(objects)
            return objects
        object = ServerObject.create(**(object))
        if fn is not None:
            object = fn(object)
        return object

    @staticmethod
    def post(uri, **kwd):
        token = PivotalObject.__token__

        data = None
        if len(kwd) > 0:
            data = {}
            for key in kwd:
                val = kwd[key]
                data[key] = val
            #data = tools.json(data)
        object = tools.http_post(uri, headers=("X-TrackerToken", token), data=data)
        if isinstance(object, basestring) is True:
            object = tools.unjson(object)

        if isinstance(object, list) is True:
            objects = [ServerObject.create(**(o)) for o in object]
            return objects
        object = ServerObject.create(**(object))
        return object


    # def _get_(self, uri):
    #     return self.__tracker__._get_(uri)
    #
    # def _post_(self, uri):
    #     return self.__tracker__._post_(uri)


    def _get_(self, uri, fn=None):
        return PivotalObject.get(uri, fn=fn)
        # request = tools.create_http_request(uri, ("X-TrackerToken", self.token))
        # object = request.GET()
        # #response = util.web_get(uri, ("X-TrackerToken", self.token))
        # #object = util.unjson(response)
        # if isinstance(object, list) is True:
        #     objects = [ServerObject.create(**(o)) for o in object]
        #     return objects
        # object = ServerObject.create(**(object))
        # return object

    def _post_(self, uri, **kwd):
        return PivotalObject.post(uri, **kwd)
        # request = tools.create_http_request(uri, ("X-TrackerToken", self.token))
        # response = request.POST()
        #
        # #response = tools.http_post(uri, headers={"X-TrackerToken": self.token})
        # object = tools.unjson(response)
        # if isinstance(object, list) is True:
        #     objects = [ServerObject.create(**(o)) for o in object]
        #     return objects
        # object = ServerObject.create(**(object))
        # return object

    # def stringify(self):
    #     tracker = self.__tracker__
    #     self.__tracker__ = None
    #     data = util.pickle(self)
    #     data = util.base64(data)
    #     self.__tracker__ = tracker
    #     return data

    # def bind(self, tracker):
    #     self.__tracker__ = tracker
    #     return self


    def deflate(self):
        tbl = self.__dict__
        obj = {}
        for key in tbl:
            if key[0] == "_":
                continue
            val = tbl[key]
            obj[key] = val

        return obj

    def __str__(self):
        try:
            return "%s [#%s] %s" % (self.__class__.__name__, str(self.id), self.label)
        except:
            return "%s #%s" % (self.__class__.__name__, str(self.id))

    def __repr__(self):
        return self.__str__()

    @classmethod
    def spawn(cls, *objects):
        objects = tools.unroll(objects)
        return [cls(**(o)) for o in objects]


class ServerObject(dict):
    def __getattr__(self, key):
        try:
            o = self[key]
            if isinstance(o, dict) is True:
                if isinstance(o, ServerObject) is False:
                    o = ServerObject.create(o)
                    self[key] = o
            elif isinstance(o, list) is True:
                if len(o) > 0:
                    if isinstance(o[0], dict) is True and isinstance(o[0], ServerObject) is False:
                        o = map(ServerObject.create, o)
                        self[key] = o
            return o
        except KeyError, ex:
            return None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            self.pop(key)
        except KeyError:
            pass

    def objectify(self):
        o = {}
        for key in self:
            val = self[key]
            if isinstance(val, list):
                if len(val) > 0 and isinstance(val[0], ServerObject) is True:
                    val = [v.objectify() for v in val]
            elif isinstance(val, ServerObject) is True:
                val = val.objectify()

            o[key] = val
        return o

    def __str__(self):
        obj = self.objectify()
        data = tools.json_encode_pretty(obj)
        return data

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def create(*args, **kwargs):
        if args and len(args) > 0:
            return ServerObject(args[0])
        return ServerObject(kwargs)


class Project(PivotalObject):
    def __init__(self, **kwd):
        PivotalObject.__init__(self, **kwd)
        self.__stories__ = None


    def fetch_story(self, id):
        stories = self.stories
        for story in stories:
            if story.id == id:
                return story
        return None

    def add_story(self, label, **kwd):
        type = kwd["type"]
        owner_ids = []

        account = kwd["account"]
        project_accounts = self.accounts
        accounts = [a for a in project_accounts if a.initials == account.initials]
        account = accounts[0]

        owner = kwd.get("owner", None)
        if owner is not None:
            accounts = [a for a in project_accounts if a.initials == owner.initials]
            owner = accounts[0]
            owner_ids.append(owner.id)

        description = kwd.get("description", None)
        estimate = kwd.get("estimate", None)

        uri = "https://www.pivotaltracker.com/services/v5/projects/{id}/stories/".format(id=self.id)
        body = {
            "project_id": self.id,
            "name": label,
            "story_type": type,
            "requested_by_id": account.id,
            "owner_ids": owner_ids
        }
        if description is not None:
            body["description"] = description

        if estimate is not None:
            body["estimate"] = estimate

        result = self._post_(uri, **(body))
        if result.get("error", None) is not None:
            message = "Error creating story: %s\n%s" % (result["error"], result["general_problem"])
            raise Exception(message)

        story = Story(**(result))
        story.project_id = self.id
        return story

    @staticmethod
    def export():
        uri = "https://www.pivotaltracker.com/services/v5/projects/"
        return PivotalObject.get(uri, fn=Project.spawn)

    @property
    def stories(self):
        if self.__stories__ is not None:
            return self.__stories__

        filter = "current_state:started,planned,unstarted,unscheduled"
        stories = self._get_(
            "https://www.pivotaltracker.com/services/v5/projects/{id}/stories/?limit=1000&filter={filter}".format(id=self.id, filter=filter),
            fn=Story.spawn
        )

        project_id = self.id
        for story in stories:
            story.project_id = project_id
        self.__stories__ = stories
        return stories

    @property
    def accounts(self):
        accounts = self._get_(
            "https://www.pivotaltracker.com/services/v5/projects/{id}/memberships".format(id=self.id),
            fn=Account.spawn
        )
        return accounts


class Story(PivotalObject):
    def __init__(self, **kwd):
        PivotalObject.__init__(self, **kwd)



class Account(PivotalObject):
    def __init__(self, **kwd):
        person = kwd.get("person", None)
        if person is not None:
            id = person["id"]
            name = person["name"]
            email = person["email"]
            username = person["username"]
            initials = person["initials"]
            kwd["name"] = name
            kwd["email"] = email
            kwd["username"] = username
            kwd["initials"] = initials
            kwd["id"] = id
            kwd["name"] = name
            kwd.pop("person")

        PivotalObject.__init__(self, **kwd)

    def is_match(self, key):
        if self.id == key:
            return True

        try:
            if self.initials.lower() == key.lower():
                return True
        except:
            pass

        try:
            if self.username.lower() == key.lower():
                return True
        except:
            pass

        try:
            if self.email.lower() == key.lower():
                return True
        except:
            pass


        try:
            if self.name.lower() == key.lower():
                return True
        except:
            pass

        return False


    def __str__(self):
        try:
            username = self.username
            return "Account#%s %s" % (str(self.id), username)
        except:
            return "Account#%s" % str(self.id)