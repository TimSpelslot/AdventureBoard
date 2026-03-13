from datetime import date

from app.models import Adventure, Assignment, Signup, User
from app.provider import db
from tests.conftest import login


def test_cancel_assignment_promotes_waiting_list_player(client, app):
    with app.app_context():
        event_date = date(2024, 6, 19)

        canceling_user = User.create(google_id="assigned-user", name="Assigned User")
        waiting_user = User.create(google_id="waiting-user", name="Waiting User")

        adventure = Adventure.create(
            title="Main Adventure",
            short_description="Main table",
            user_id=canceling_user.id,
            max_players=1,
            date=event_date,
            is_waitinglist=0,
        )

        waiting_list_adventure = Adventure.create(
            title="Waiting List",
            short_description="Fallback table",
            user_id=canceling_user.id,
            max_players=99,
            date=event_date,
            is_waitinglist=1,
        )

        db.session.add(
            Assignment(
                user_id=canceling_user.id,
                adventure_id=adventure.id,
                preference_place=1,
            )
        )
        db.session.add(
            Assignment(
                user_id=waiting_user.id,
                adventure_id=waiting_list_adventure.id,
            )
        )
        db.session.add(
            Signup(
                user_id=waiting_user.id,
                adventure_id=adventure.id,
                priority=1,
                adventure_date=event_date,
            )
        )
        db.session.commit()

        canceling_user_id = canceling_user.id
        waiting_user_id = waiting_user.id
        adventure_id = adventure.id
        waiting_list_adventure_id = waiting_list_adventure.id

    login(client, canceling_user_id)

    response = client.delete(
        "/api/player-assignments",
        json={"adventure_id": adventure_id},
        base_url="https://localhost",
    )

    assert response.status_code == 200

    with app.app_context():
        canceled_assignment = db.session.scalar(
            db.select(Assignment).where(
                Assignment.user_id == canceling_user_id,
                Assignment.adventure_id == adventure_id,
            )
        )
        assert canceled_assignment is None

        promoted_assignment = db.session.scalar(
            db.select(Assignment).where(
                Assignment.user_id == waiting_user_id,
                Assignment.adventure_id == adventure_id,
            )
        )
        assert promoted_assignment is not None

        waiting_list_assignment = db.session.scalar(
            db.select(Assignment).where(
                Assignment.user_id == waiting_user_id,
                Assignment.adventure_id == waiting_list_adventure_id,
            )
        )
        assert waiting_list_assignment is None
