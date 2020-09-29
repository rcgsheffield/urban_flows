import http_session
import objects

if __name__ == '__main__':
    session = http_session.PortalSession()

    for obj in objects.AQIStandard.list(session):
        print(obj)
