from hendrix.ux import launch
from hendrix.deploy.base import HendrixDeploy


if __name__ == "__main__":
    options = {'settings': 'settings.local'}
    deployer = HendrixDeploy(options=options)
    deployer.run()