"""Testing not_found.py"""

from __future__ import unicode_literals
import pytest
from pyramid.httpexceptions import HTTPFound
from pyramid import testing



def test_not_found(app):
    response = app.get('/not_found', status='4*')
    assert response.status_code == 404
