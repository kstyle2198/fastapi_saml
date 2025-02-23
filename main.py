from fastapi import FastAPI, Request, Depends, Response, HTTPException, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from saml_config import get_saml_settings
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend domain for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable session middleware
app.add_middleware(SessionMiddleware, secret_key="771bddefddaf2a12996211a663a61663bfd4c2a8fc8931e0bb0e20d104e79729", session_cookie="session_id")

def prepare_saml_request(request: Request):
    """Prepare SAML authentication request from FastAPI request."""
    url_data = request.url.components
    return {
        "https": "on" if request.url.scheme == "https" else "off",
        "http_host": url_data.netloc,
        "script_name": url_data.path,
        "server_port": 443 if request.url.scheme == "https" else 80,
        "get_data": request.query_params,
        "post_data": request.form(),
    }


@app.post("/login", tags=["Session Test"])
async def login(response: Response, user_id:str):
    # Set a cookie in the response
    response.set_cookie(key="session_id", value=user_id, httponly=True)
    return {"message": f"ID {user_id} Login successful, cookie set"}


@app.get("/check-cookie", tags=["Session Test"])
async def check_cookie(request: Request, cookie_name: str = "session_id"):
    # Get cookies from request
    cookies = request.cookies
    # Check if the specific cookie exists
    if cookie_name in cookies:
        print(f"Cookie '{cookie_name}' found! Redirect to Service Page")
        return {'message': 'success'}
    else:
        print(f"Cookie '{cookie_name}' found! Redirect to Login Page")
        return {'message': 'fail'}


############################################################################################################


@app.get("/", response_class=HTMLResponse, tags=["SAML Test"])
async def home(request: Request):
    """Home page with login button."""
    return """<html><body><a href="/sso/login/">Login with SAML</a></body></html>"""

@app.get("/metadata/", tags=["SAML Test"])
def metadata():
    """SAML 서비스 제공자(SP)의 메타데이터(XML 형식)를 반환하는 엔드포인트"""
    settings = get_saml_settings()
    metadata = settings.get_sp_metadata()
    return Response(content=metadata, media_type="application/xml")

@app.get("/sso/login/", tags=["SAML Test"])
async def saml_login(request: Request):
    """
    Redirect users to SAML login page(IdP, Identity Provider).
    OneLogin_Saml2_Auth 객체를 생성하여 auth.login()을 호출하면, 사용자는 IdP의 로그인 페이지로 이동
    """
    auth = OneLogin_Saml2_Auth(prepare_saml_request(request), get_saml_settings())

    print(f">>> name_id : {auth.get_nameid()}")
    print(f">>> is_authenticated : {auth.is_authenticated()}")
    print(f">>> get_attributes : {auth.get_attributes()}")
    print(f">>> get_friendlyname_attributes : {auth.get_friendlyname_attributes()}")
    print(f">>> sso url : {auth.get_sso_url()}")
    print(f">>> slo url : {auth.get_slo_url()}")
    print(f">>> get_errors : {auth.get_errors()}")

    return RedirectResponse(auth.login())

@app.post("/sso/acs/", tags=["SAML Test"])
async def saml_acs(request: Request):
    """
    Handle SAML Authentication Response (Assertion Consumer Service).
    IdP로부터 받은 SAML 응답을 처리하고, 사용자 인증 여부를 확인합니다.
    인증이 성공하면 세션에 "user" 정보를 저장하고 대시보드로 리디렉션합니다.
    """
    auth = OneLogin_Saml2_Auth(prepare_saml_request(request), get_saml_settings())

    print(f">>> name_id : {auth.get_nameid()}")
    print(f">>> is_authenticated : {auth.is_authenticated()}")
    print(f">>> get_attributes : {auth.get_attributes()}")
    print(f">>> get_friendlyname_attributes : {auth.get_friendlyname_attributes()}")
    print(f">>> sso url : {auth.get_sso_url()}")
    print(f">>> slo url : {auth.get_slo_url()}")
    print(f">>> get_errors : {auth.get_errors()}")

    auth.process_response() # Process the SAML Response sent by the IdP.

    if auth.is_authenticated():  # Checks if the user is authenticated or not.
        request.session["user"] = auth.get_nameid()  # Returns the nameID.
        return RedirectResponse("/dashboard/")
    
    return HTMLResponse("<h1>Authentication Failed</h1>")

@app.get("/dashboard/", tags=["SAML Test"])
async def dashboard(request: Request):
    """
    Authenticated user dashboard.
    세션에서 로그인된 user 정보를 가져와서 대시보드를 표시
    로그인되지 않은 경우 홈 페이지로 리디렉션
    """
    user = request.session.get("user")
    print(f">>> request.session: {request.session}")
    if user:
        return HTMLResponse(f"<h1>Welcome {user}!</h1>")
    return RedirectResponse("/")

@app.get("/sso/logout/", tags=["SAML Test"])
async def saml_logout(request: Request, cookie_name: str = "session_id"):
    """
    session_id 쿠키 존재 여부 확인후, 존재하면 서비스 페이지로 리디렉션, 없으면 idp 로긴 페이지로 리디렉션
    """

    # Get cookies from request
    cookies = request.cookies
    # Check if the specific cookie exists
    if cookie_name in cookies:
        print(f">>> Cookie '{cookie_name}' found! Redirect to Service Page")
        return RedirectResponse("/")
    else:
        print(f">>> Cookie '{cookie_name}' found! Redirect to Login Page")
        auth = OneLogin_Saml2_Auth(prepare_saml_request(request), get_saml_settings())
        return RedirectResponse(auth.logout())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    