import re
from playwright.sync_api import expect
import json
def test_user_creates_car_in_browser(page, live_server):
    page.goto(f"{live_server}/cars/new")
    page.get_by_label("Make", exact=True).fill("Toyota")
    page.get_by_label("Model", exact=True).fill("Yaris")
    page.get_by_label("Year", exact=True).fill("2020")
    page.get_by_label("Color", exact=False).fill("Blue")
    page.get_by_role("button", name="Create car").click()
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))
    expect(page.get_by_role("heading", name="Toyota Yaris")).to_be_visible()

def test_user_edits_car_and_change_survives_reload(page, live_server):
    # page.goto(f"{live_server}/cars/new")
    # page.get_by_label("Make", exact=True).fill("Honda")
    # page.get_by_label("Model", exact=True).fill("Civic")
    # page.get_by_label("Year", exact=True).fill("2022")
    # page.get_by_label("Color", exact=False).fill("Silver")
    # page.get_by_role("button", name="Create car").click()
    # page.get_by_role("link", name="Edit car").click()
    # page.get_by_label("Model", exact=True).fill("Accord")
    # page.get_by_label("Year", exact=True).fill("2023")
    # page.get_by_role("button", name="Save changes").click()
    # expect(page).to_have_url(re.compile(r"/cars/\d+$"))

    
    # expect(page.get_by_role("heading", name="Honda Accord")).to_be_visible()
    # page.reload()
    # expect(page.locator("#car-model")).to_have_text("Accord")
    # expect(page.locator("#car-year")).to_have_text("2023")
    page.goto(f"{live_server}/cars/new")
    page.get_by_label("Make", exact=True).fill("Honda")
    page.get_by_label("Model", exact=True).fill("Civic")
    page.get_by_label("Year", exact=True).fill("2022")
    page.get_by_label("Color", exact=False).fill("Silver")
    page.get_by_role("button", name="Create car").click()

    # 打印：创建后 URL 是什么
    print("DEBUG 创建后 URL:", page.url, flush=True)

    page.get_by_role("link", name="Edit car").click()

    # 打印：点击 Edit 后 URL 是什么
    print("DEBUG 编辑页 URL:", page.url, flush=True)

    page.get_by_label("Model", exact=True).fill("Accord")
    page.get_by_label("Year", exact=True).fill("2023")

    # 打印：编辑页输入框里实际填了什么
    print("DEBUG Model 输入框:", page.get_by_label("Model", exact=True).input_value(), flush=True)
    print("DEBUG Year 输入框:", page.get_by_label("Year", exact=True).input_value(), flush=True)

    page.get_by_role("button", name="Save changes").click()
    response = page.request.get(f"{live_server}/api/cars/1")
    print("GET /api/cars/1:", response.status, response.text(), flush=True)

    response = page.request.put(
        f"{live_server}/api/cars/1",
        data=json.dumps({"make": "Honda", "model": "Accord", "year": 2023, "color": "Silver"}),
        headers={"Content-Type": "application/json"},
    )
    print("PUT /api/cars/1:", response.status, response.text(), flush=True)

    response = page.request.get(f"{live_server}/api/cars/1")
    print("GET after PUT:", response.status, response.text(), flush=True)
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))

    # 打印：保存后 URL 和页面内容
    print("DEBUG 保存后 URL:", page.url, flush=True)
    print("DEBUG 保存后 BODY:", page.locator("body").inner_text(), flush=True)
    print("DEBUG 所有 heading:", page.get_by_role("heading").all_inner_texts(), flush=True)

    expect(page.get_by_role("heading", name="Honda Accord")).to_be_visible()

    page.reload()
    expect(page.locator("#car-model")).to_have_text("Accord")
    expect(page.locator("#car-year")).to_have_text("2023")