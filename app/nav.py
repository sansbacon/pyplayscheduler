from flask_nav import Nav
from flask_nav.elements import Navbar, View


nav = Nav()

topbar = Navbar('',
    View('Settings', 'setup'),
    View('Schedule', 'schedule'),
    View('Summary', 'summary')
)

nav.register_element('top', topbar)