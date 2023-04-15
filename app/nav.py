from flask_nav import Nav
from flask_nav.elements import Navbar, View


nav = Nav()

topbar = Navbar('',
    View('Settings', 'blueprint.index'),
    View('Schedule', 'blueprint.schedule'),
    View('Summary', 'blueprint.summary')
)

nav.register_element('top', topbar)