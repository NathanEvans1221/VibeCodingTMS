import itertools
import unittest

import app as tms


class TMSRouteTests(unittest.TestCase):
    def setUp(self):
        tms.cargo_data.clear()
        tms.routes_data.clear()
        tms.shipments_data.clear()
        tms._cargo_ids = itertools.count(1)
        tms._route_ids = itertools.count(1)
        tms._shipment_ids = itertools.count(1)
        tms.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = tms.app.test_client()

    def test_new_cargo_id_does_not_collide_after_delete(self):
        first = tms.Cargo("第一件", 1, 1)
        second = tms.Cargo("第二件", 1, 1)
        tms.cargo_data.extend([first, second])
        tms.cargo_data.remove(first)

        response = self.client.post(
            "/cargo/add",
            data={"name": "第三件", "quantity": "1", "weight": "1"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len({cargo.id for cargo in tms.cargo_data}), 2)
        self.assertEqual(tms.cargo_data[-1].id, 3)

    def test_invalid_cargo_input_is_rejected_without_server_error(self):
        response = self.client.post(
            "/cargo/add",
            data={"name": "   ", "quantity": "0", "weight": "-1"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(tms.cargo_data, [])

    def test_cannot_delete_cargo_referenced_by_shipment(self):
        cargo = tms.Cargo("貨物", 1, 1)
        route = tms.Route("路線", "起點", "終點")
        tms.cargo_data.append(cargo)
        tms.routes_data.append(route)
        tms.shipments_data.append(tms.Shipment(cargo.id, route.id))

        response = self.client.post(f"/cargo/delete/{cargo.id}")

        self.assertEqual(response.status_code, 302)
        self.assertIn(cargo, tms.cargo_data)
        self.assertEqual(len(tms.shipments_data), 1)

    def test_cannot_delete_route_referenced_by_shipment(self):
        cargo = tms.Cargo("貨物", 1, 1)
        route = tms.Route("路線", "起點", "終點")
        tms.cargo_data.append(cargo)
        tms.routes_data.append(route)
        tms.shipments_data.append(tms.Shipment(cargo.id, route.id))

        response = self.client.post(f"/routes/delete/{route.id}")

        self.assertEqual(response.status_code, 302)
        self.assertIn(route, tms.routes_data)
        self.assertEqual(len(tms.shipments_data), 1)

    def test_invalid_route_input_is_rejected(self):
        response = self.client.post(
            "/routes/add",
            data={"name": "路線", "start_point": " ", "end_point": "終點"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(tms.routes_data, [])

    def test_invalid_shipment_ids_are_rejected(self):
        response = self.client.post(
            "/shipments/assign", data={"cargo_id": "bad", "route_id": "1"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(tms.shipments_data, [])

    def test_list_pages_render_post_write_controls(self):
        cargo = tms.Cargo("貨物", 1, 1)
        route = tms.Route("路線", "起點", "終點")
        tms.cargo_data.append(cargo)
        tms.routes_data.append(route)
        tms.shipments_data.append(tms.Shipment(cargo.id, route.id))

        for path in ("/cargo", "/routes", "/shipments"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'method="POST"', response.data)

    def test_delete_requires_post(self):
        response = self.client.get("/cargo/delete/1")

        self.assertEqual(response.status_code, 405)

    def test_status_update_requires_post_and_valid_transition(self):
        shipment = tms.Shipment(1, 1)
        tms.shipments_data.append(shipment)

        get_response = self.client.get(
            f"/shipments/update_status/{shipment.id}/配送中"
        )
        invalid_response = self.client.post(
            f"/shipments/update_status/{shipment.id}/已送達"
        )
        valid_response = self.client.post(
            f"/shipments/update_status/{shipment.id}/配送中"
        )

        self.assertEqual(get_response.status_code, 405)
        self.assertEqual(invalid_response.status_code, 302)
        self.assertEqual(valid_response.status_code, 302)
        self.assertEqual(shipment.status, "配送中")


if __name__ == "__main__":
    unittest.main()
