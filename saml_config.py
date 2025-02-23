import os
from onelogin.saml2.settings import OneLogin_Saml2_Settings


def get_saml_settings():
    """Generate SAML settings for the Service Provider (SP)."""
    
    settings = {
        "strict": True,
        "debug": True,

        # Service Provider (SP) Configuration
        "sp": {
            "entityId": "http://localhost:8000/metadata/",
            "assertionConsumerService": {
                "url": "http://localhost:8000/sso/acs/",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "singleLogoutService": {
                "url": "http://localhost:8000/sso/logout/",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "x509cert": open("certs/sp.cert").read(),
            "privateKey": open("certs/sp.key").read(),
        },

        # Identity Provider (IdP) Configuration
        "idp": {
            "entityId": "https://idp.example.com/metadata",
            "singleSignOnService": {
                "url": "https://idp.example.com/sso",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "singleLogoutService": {
                "url": "https://idp.example.com/slo",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "x509cert": "YOUR_IDP_CERTIFICATE_HERE",
        },
    }
    
    return OneLogin_Saml2_Settings(settings)
