import unittest
from io import BytesIO
from PIL import Image
from agroroute.farm import demo_farm
from agroroute.autonomous import build_workflow, start_rover, simulate_to_completion, workflow_report, validate_image

def img():
    buf=BytesIO()
    Image.new("RGB",(32,32),"green").save(buf,format="PNG")
    return buf.getvalue()

def fake_predictor(model_dir, content):
    return "Early_blight", 0.91, {"Early_blight":0.91,"Healthy":0.09}

class TestAutonomousWorkflow(unittest.TestCase):
    def test_existing_zones_complete(self):
        result=build_workflow(demo_farm(),planner="Nearest Neighbor")
        self.assertTrue(result.ready)
        rover=simulate_to_completion(result,0.4,20)
        self.assertEqual(rover.status,"Completed")
        self.assertEqual(len(rover.inspected),4)
        self.assertEqual(rover.position,result.farm.rover)
        self.assertEqual(workflow_report(result,rover)["rover"]["status"],"Completed")
    def test_predict_and_add_zone_without_mutation(self):
        farm=demo_farm()
        result=build_workflow(farm,image_bytes=img(),zone=(3,3),
                              predictor=fake_predictor,planner="Nearest Neighbor")
        self.assertEqual(farm.cells[3][3],"crop")
        self.assertEqual(result.farm.cells[3][3],"infected")
        self.assertEqual(result.overview["total_zones"],5)
        self.assertEqual(result.diagnoses["3,3"]["class"],"Early_blight")
        self.assertTrue(result.ready)
    def test_low_probability_requires_review(self):
        result=build_workflow(demo_farm(),image_bytes=img(),zone=(3,3),
                              predictor=lambda *_:("Late_blight",0.5,{}),
                              planner="Nearest Neighbor")
        self.assertGreaterEqual(result.overview["manual_review"],1)
    def test_healthy_does_not_create_zone(self):
        result=build_workflow(demo_farm(),image_bytes=img(),zone=(3,3),
                              predictor=lambda *_:("Healthy",0.95,{}),
                              planner="Nearest Neighbor")
        self.assertEqual(result.overview["total_zones"],4)
    def test_blocked_mission_cannot_start(self):
        result=build_workflow(demo_farm(),planner="Nearest Neighbor",reserve=99)
        self.assertFalse(result.ready)
        with self.assertRaises(ValueError):
            start_rover(result,20)
    def test_invalid_zone(self):
        with self.assertRaises(ValueError):
            build_workflow(demo_farm(),image_bytes=img(),zone=(3,5),predictor=fake_predictor)
    def test_invalid_image(self):
        with self.assertRaises(ValueError):
            validate_image(b"not an image")
    def test_image_too_large(self):
        with self.assertRaises(ValueError):
            validate_image(b"x"*15, max_bytes=10)
