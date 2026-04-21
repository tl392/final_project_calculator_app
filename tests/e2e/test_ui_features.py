from uuid import uuid4


def _register(page, base_url, username, email, password="SecurePass123!"):
    page.goto(f"{base_url}/register")
    page.fill("#username", username)
    page.fill("#email", email)
    page.fill("#first_name", "UI")
    page.fill("#last_name", "Tester")
    page.fill("#password", password)
    page.fill("#confirm_password", password)
    page.click("button[type='submit']")
    page.wait_for_url(f"{base_url}/login")


def _login(page, base_url, username, password="SecurePass123!"):
    page.goto(f"{base_url}/login")
    page.fill("#username", username)
    page.fill("#password", password)
    page.click("button[type='submit']")
    page.wait_for_url(f"{base_url}/dashboard")


def test_ui_exponentiation_and_reports(page, fastapi_server):
    base_url = fastapi_server.rstrip('/')
    username = f"ui_user_{uuid4().hex[:8]}"
    email = f"{username}@example.com"

    _register(page, base_url, username, email)
    _login(page, base_url, username)

    page.select_option("#calcType", "exponentiation")
    page.fill("#calcInputs", "2, 3")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    assert "8" in page.locator("#calculationsTable").inner_text()

    page.select_option("#calcType", "sqrt")
    page.fill("#calcInputs", "81")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    assert "9" in page.locator("#calculationsTable").inner_text()

    page.goto(f"{base_url}/reports")
    page.wait_for_timeout(500)
    assert username in page.locator("#userSummary").inner_text()
    assert page.locator("#totalCalculations").inner_text() == "2"


def test_ui_modulus_negative_scenario(page, fastapi_server):
    base_url = fastapi_server.rstrip('/')
    username = f"ui_mod_{uuid4().hex[:8]}"
    email = f"{username}@example.com"

    _register(page, base_url, username, email)
    _login(page, base_url, username)

    page.select_option("#calcType", "modulus")
    page.fill("#calcInputs", "10, 0")
    page.click("button[type='submit']")
    page.wait_for_timeout(500)
    assert "modulus by zero" in page.locator("#messageBox").inner_text().lower()
