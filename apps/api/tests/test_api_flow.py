import uuid

def test_health_check(client):
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ResQNet" in data["app"]

def test_end_to_end_sos_and_routing_pipeline(client):
    # 1. Submit a raw Hinglish SOS report
    client_uuid = str(uuid.uuid4())
    sos_payload = {
        "client_uuid": client_uuid,
        "source": "whatsapp",
        "raw_text": "paani bhar gaya hai near sector 5, 5 log chhat par hain please madad karo"
    }
    create_res = client.post("/v1/sos", json=sos_payload)
    assert create_res.status_code == 202
    sos_data = create_res.json()
    assert sos_data["client_uuid"] == client_uuid
    assert sos_data["language"] == "Hinglish"
    assert sos_data["extracted"]["need_type"] == "Rescue"
    assert sos_data["extracted"]["people_count"] == 5
    assert "Sector 5" in (sos_data["extracted"]["location_text"] or "")
    report_id = sos_data["id"]

    # 2. Check Verification Queue
    queue_res = client.get("/v1/sos?status=pending")
    assert queue_res.status_code == 200
    queue_data = queue_res.json()
    assert queue_data["total"] >= 1
    assert any(item["id"] == report_id for item in queue_data["items"])

    # 3. Coordinator verifies the SOS report
    verify_res = client.patch(f"/v1/sos/{report_id}/verify")
    assert verify_res.status_code == 200
    verified_data = verify_res.json()
    assert verified_data["status"] == "verified"
    assert verified_data["incident_id"] is not None
    incident_id = verified_data["incident_id"]

    # 4. Check incidents endpoint
    inc_res = client.get("/v1/incidents")
    assert inc_res.status_code == 200
    inc_list = inc_res.json()
    assert any(inc["id"] == incident_id for inc in inc_list)

    # 5. Get available resources and plan route
    res_list_resp = client.get("/v1/resources")
    assert res_list_resp.status_code == 200
    resources = res_list_resp.json()
    assert len(resources) > 0
    resource_id = resources[0]["id"]

    plan_res = client.post("/v1/routes/plan", json={
        "resource_id": resource_id,
        "incident_id": incident_id
    })
    assert plan_res.status_code == 200
    plan_data = plan_res.json()
    assert plan_data["distance_km"] > 0
    assert plan_data["eta_minutes"] > 0
    assert plan_data["route_geojson"]["type"] == "LineString"
    initial_distance = plan_data["distance_km"]

    # 6. Block a critical road edge and verify dynamic re-routing
    roads_res = client.get("/v1/roads")
    assert roads_res.status_code == 200
    roads = roads_res.json()
    target_edge = roads[0]["id"]

    block_res = client.post(f"/v1/roads/{target_edge}/block", json={"reported_by": "coordinator_demo"})
    assert block_res.status_code == 200
    block_data = block_res.json()
    assert block_data["is_blocked"] is True

    # 7. Unblock the road edge
    unblock_res = client.delete(f"/v1/roads/{target_edge}/block")
    assert unblock_res.status_code == 200
    assert unblock_res.json()["is_blocked"] is False

