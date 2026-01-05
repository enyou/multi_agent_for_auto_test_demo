import pytest
from playwright.sync_api import Page, expect


def test_TC_F_4aa9ded3_001(page: Page):
    # 访问登录页面
    page.goto("http://localhost:5173/login")
    
    # 等待页面加载完成
    page.wait_for_load_state("networkidle")
    
    # 输入手机号
    username_input = page.locator("#username")
    username_input.wait_for(state="visible")
    username_input.fill("13800138000")
    
    # 输入密码
    password_input = page.locator("#password")
    password_input.wait_for(state="visible")
    password_input.fill("pass1234")
    
    # 点击登录按钮
    login_button = page.locator("button.login-btn")
    login_button.wait_for(state="visible")
    login_button.click()
    
    # 等待登录请求完成
    page.wait_for_load_state("networkidle")
    
    # 断言：验证登录成功，检查是否返回token
    # 这里假设登录成功后会在localStorage中设置token
    token = page.evaluate("() => localStorage.getItem('token')")
    assert token is not None, "登录失败，未获取到token"
    assert len(token) > 0, "登录失败，token为空"
    
    # 或者检查页面跳转（如果登录成功会跳转到其他页面）
    # current_url = page.url
    # assert current_url != "http://localhost:5173/login", "登录失败，仍然停留在登录页面"