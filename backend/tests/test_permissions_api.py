from datetime import date

from app.models import Adventure, Assignment, User
from app.provider import db
from tests.conftest import login


def _create_adventure_with_assignment(app):
    with app.app_context():
        approved = User.create(google_id="approved-user", name="Approved", privilege_level=1)
        other = User.create(google_id="other-user", name="Other", privilege_level=1)

        adventure = Adventure.create(
            title="Permission Session",
            short_description="Permission test",
            user_id=approved.id,
            max_players=5,
            date=date(2026, 3, 20),
            tags=None,
            is_waitinglist=0,
            commit=False,
        )
        db.session.add(Assignment(user_id=other.id, adventure_id=adventure.id))
        db.session.commit()

        return adventure.id, approved.id


def test_assignment_users_forbidden_for_privilege_zero(client, app, normal_user_id):
    adventure_id, _ = _create_adventure_with_assignment(app)
    login(client, normal_user_id)

    response = client.get(
        f"/api/player-assignments?adventure_id={adventure_id}",
        base_url="https://localhost",
    )

    assert response.status_code == 401


def test_assignment_users_visible_for_privilege_one(client, app):
    adventure_id, approved_id = _create_adventure_with_assignment(app)
    login(client, approved_id)

    response = client.get(
        f"/api/player-assignments?adventure_id={adventure_id}",
        base_url="https://localhost",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["display_name"] == "Other"


def test_adventure_list_hides_assignments_for_privilege_zero(client, app, normal_user_id):
    _create_adventure_with_assignment(app)
    login(client, normal_user_id)

    response = client.get(
        "/api/adventures?week_start=2026-03-16&week_end=2026-03-22",
        base_url="https://localhost",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    assert "assignments" not in data[0]


def test_adventure_list_shows_assignments_for_privilege_one(client, app):
    _, approved_id = _create_adventure_with_assignment(app)
    login(client, approved_id)

    response = client.get(
        "/api/adventures?week_start=2026-03-16&week_end=2026-03-22",
        base_url="https://localhost",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    assert "assignments" in data[0]


def test_adventure_create_forbidden_for_privilege_zero(client, normal_user_id):
    login(client, normal_user_id)

    response = client.post(
        "/api/adventures",
        json={
            "title": "Blocked Session",
            "short_description": "Should fail",
            "max_players": 5,
            "date": "2026-03-20",
        },
        base_url="https://localhost",
    )

    assert response.status_code == 401


def test_adventure_create_allowed_for_privilege_one(client, app):
    with app.app_context():
        approved = User.create(google_id="creator-user", name="Creator", privilege_level=1)
        approved_id = approved.id

    login(client, approved_id)

    response = client.post(
        "/api/adventures",
        json={
            "title": "Allowed Session",
            "short_description": "Should succeed",
            "max_players": 5,
            "date": "2026-03-20",
        },
        base_url="https://localhost",
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Allowed Session"


def test_non_admin_cannot_promote_user_to_admin(client, app, normal_user_id):
    with app.app_context():
        target = User.create(google_id="target-user", name="Target", privilege_level=1)
        target_id = target.id

    login(client, normal_user_id)

    response = client.patch(
        f"/api/users/{target_id}",
        json={"privilege_level": 2},
        base_url="https://localhost",
    )

    assert response.status_code == 401


def test_admin_can_promote_user_to_admin(client, app, admin_user_id):
    with app.app_context():
        target = User.create(google_id="target-admin-user", name="Target Admin", privilege_level=1)
        target_id = target.id

    login(client, admin_user_id)

    response = client.patch(
        f"/api/users/{target_id}",
        json={"privilege_level": 2},
        base_url="https://localhost",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["privilege_level"] == 2
