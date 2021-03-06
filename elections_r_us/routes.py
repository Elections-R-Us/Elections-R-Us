"""Routes for this website."""


def includeme(config):
    """Routes for this website."""
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('results_list', '/results_list')
    config.add_route('candidate_cards', '/candidate_cards')
    config.add_route('detail', '/detail')
    config.add_route('user_profile', '/user_profile')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('change_password', '/change_password')
    config.add_route('about_us', '/about_us')
    config.add_route('favorite', '/favorite')
