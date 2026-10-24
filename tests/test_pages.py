from django.contrib.messages import constants
from django.contrib.messages.storage.base import Message
from django.contrib.messages.storage.cookie import CookieStorage
from django.urls import reverse


def test_home_page_renders_from_the_base_template(client):
    response = client.get(reverse("home"), secure=True)
    assert response.status_code == 200
    assert [t.name for t in response.templates][:2] == ["home.html", "base.html"]
    html = response.content.decode()
    assert '<html lang="en-us">' in html
    assert 'name="viewport" content="width=device-width, initial-scale=1"' in html
    assert "<h1>Academic events, open to you</h1>" in html
    assert 'href="#main"' in html


def test_base_template_shows_messages(client, rf):
    encoded = CookieStorage(rf.get("/"))._encode([Message(constants.SUCCESS, "Saved.")])
    client.cookies["messages"] = encoded
    html = client.get(reverse("home"), secure=True).content.decode()
    assert '<p class="message message-success">Saved.</p>' in html
