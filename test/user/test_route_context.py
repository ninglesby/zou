from test.base import ApiDBTestCase

from zou.app.models.task import Task


class UserContextRoutesTestCase(ApiDBTestCase):

    def setUp(self):
        super(UserContextRoutesTestCase, self).setUp()
        self.generate_fixture_project_status()
        self.generate_fixture_project_closed_status()
        self.generate_fixture_project()
        self.generate_fixture_person()
        self.generate_fixture_project_closed()
        self.generate_fixture_entity_type()
        self.generate_fixture_entity()
        self.generate_fixture_sequence()
        self.generate_fixture_shot()
        self.generate_fixture_department()
        self.generate_fixture_task_type()
        self.generate_fixture_task_status()
        self.generate_fixture_assigner()
        self.generate_fixture_task()
        self.entity_dict = self.entity.serialize(obj_type="Asset")
        self.maxDiff = None

        self.task_id = self.task.id
        self.project_closed_id = self.project_closed.id

    def assign_user(self, task_id):
        task = Task.get(task_id)
        task.assignees.append(self.user)

    def test_get_project_sequences(self):
        self.generate_fixture_shot_task()
        self.assign_user(self.shot_task.id)
        sequences = self.get(
            "data/user/projects/%s/sequences" % self.project.id
        )
        self.assertEquals(len(sequences), 1)

    def test_get_sequence_shots(self):
        self.generate_fixture_shot_task()
        self.assign_user(self.shot_task.id)
        shots = self.get("data/user/sequences/%s/shots" % self.sequence.id)
        self.assertEquals(len(shots), 1)

    def test_get_project_asset_types(self):
        task_id = self.task.id
        self.generate_fixture_shot_task()
        shot_task_id = self.shot_task.id
        self.generate_fixture_asset_types()
        self.generate_fixture_entity_character()
        self.generate_fixture_task("main", self.entity_character.id)
        task2_id = self.task.id
        self.generate_fixture_task("second", self.entity_character.id)
        task3_id = self.task.id

        asset_types = self.get(
            "data/user/projects/%s/asset-types" % self.project.id
        )
        self.assertEquals(len(asset_types), 0)

        self.assign_user(task_id)
        self.assign_user(task2_id)
        self.assign_user(task3_id)
        self.assign_user(shot_task_id)
        asset_types = self.get(
            "data/user/projects/%s/asset-types" % self.project.id
        )
        self.assertEquals(len(asset_types), 2)

    def test_get_project_asset_types_assets(self):
        task_id = self.task.id
        assets = self.get(
            "data/user/projects/%s/asset-types/%s/assets" % (
                self.project.id,
                self.entity_type.id
            )
        )
        self.assertEquals(len(assets), 0)
        self.assign_user(task_id)

        assets = self.get(
            "data/user/projects/%s/asset-types/%s/assets" % (
                self.project.id,
                self.entity_type.id
            )
        )
        self.assertEquals(len(assets), 1)

    def test_get_asset_tasks(self):
        path = "data/user/assets/%s/tasks" % self.entity.id
        task_id = self.task.id

        tasks = self.get(path)
        self.assertEquals(len(tasks), 0)

        self.assign_user(task_id)
        tasks = self.get(path)
        self.assertEquals(len(tasks), 1)

    def test_get_shot_tasks(self):
        path = "data/user/shots/%s/tasks" % self.shot.id
        self.generate_fixture_shot_task()
        shot_task_id = self.shot_task.id

        tasks = self.get(path)
        self.assertEquals(len(tasks), 0)

        self.assign_user(shot_task_id)
        tasks = self.get(path)
        self.assertEquals(len(tasks), 1)

    def test_get_open_projects(self):
        projects = self.get("data/user/projects/open")
        self.assertEquals(len(projects), 0)

        task = Task.get(self.task_id)
        task.assignees = [self.user]
        task.save()

        projects = self.get("data/user/projects/open")
        self.assertEquals(len(projects), 1)

        task.project_id = self.project_closed_id
        task.save()
        projects = self.get("data/user/projects/open")
        self.assertEquals(len(projects), 0)