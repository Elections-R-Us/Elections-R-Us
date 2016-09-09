"""Testing not_found.py"""


def test_not_found(app):
    """Test not_found returns a 404 response"""
    response = app.get('/not_found', status='4*')
    assert response.status_code == 404
