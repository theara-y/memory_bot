def test_login(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert '<button>Login</button>' in response.data.decode('utf-8')

def test_register(client):
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert '<button>Register</button>' in response.data.decode('utf-8')