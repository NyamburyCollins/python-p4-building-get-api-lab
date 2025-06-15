import json
from os import environ
import re

from app import app
from models import db, Bakery, BakedGood

class TestApp:
    '''Flask application in flask_app.py'''

    def test_bakeries_route(self):
        '''has a resource available at "/bakeries".'''
        response = app.test_client().get('/bakeries')
        assert response.status_code == 200

    def test_bakeries_route_returns_json(self):
        '''provides a response content type of application/json at "/bakeries"'''
        response = app.test_client().get('/bakeries')
        assert response.content_type == 'application/json'

    def test_bakeries_route_returns_list_of_bakery_objects(self):
        '''returns JSON representing models.Bakery objects.'''
        with app.app_context():
            b = Bakery(name="My Bakery")
            db.session.add(b)
            db.session.commit()

            response = app.test_client().get('/bakeries')
            data = json.loads(response.data)
            assert isinstance(data, list)

            contains_my_bakery = any(record.get('name') == "My Bakery" for record in data)
            assert contains_my_bakery

            db.session.delete(b)
            db.session.commit()

    def test_bakery_by_id_route(self):
        '''has a resource available at "/bakeries/<int:id>".'''
        with app.app_context():
            b = Bakery(name="My Bakery")
            db.session.add(b)
            db.session.commit()

            response = app.test_client().get(f'/bakeries/{b.id}')
            assert response.status_code == 200

            db.session.delete(b)
            db.session.commit()

    def test_bakery_by_id_route_returns_json(self):
        '''provides a response content type of application/json at "/bakeries/<int:id>"'''
        with app.app_context():
            b = Bakery(name="My Bakery")
            db.session.add(b)
            db.session.commit()

            response = app.test_client().get(f'/bakeries/{b.id}')
            assert response.content_type == 'application/json'

            db.session.delete(b)
            db.session.commit()

    def test_bakery_by_id_route_returns_one_bakery_object(self):
        '''returns JSON representing one models.Bakery object.'''
        with app.app_context():
            b = Bakery(name="My Bakery")
            db.session.add(b)
            db.session.commit()

            response = app.test_client().get(f'/bakeries/{b.id}')
            data = json.loads(response.data)
            assert isinstance(data, dict)
            assert data['id'] == b.id
            assert data['name'] == "My Bakery"
            assert 'created_at' in data

            db.session.delete(b)
            db.session.commit()

    def test_baked_goods_by_price_route(self):
        '''has a resource available at "/baked_goods/by_price".'''
        response = app.test_client().get('/baked_goods/by_price')
        assert response.status_code == 200

    def test_baked_goods_by_price_route_returns_json(self):
        '''provides a response content type of application/json at "/baked_goods/by_price"'''
        response = app.test_client().get('/baked_goods/by_price')
        assert response.content_type == 'application/json'

    def test_baked_goods_by_price_returns_list_of_baked_goods_in_descending_order(self):
        '''returns JSON list of BakedGood objects sorted by price (desc).'''
        with app.app_context():
            prices = [bg.price for bg in BakedGood.query.all()]
            highest_price = max(prices) if prices else 0

            b1 = BakedGood(name="Madeleine", price=highest_price + 1)
            b2 = BakedGood(name="Donut", price=highest_price - 1)
            db.session.add_all([b1, b2])
            db.session.commit()

            response = app.test_client().get('/baked_goods/by_price')
            data = json.loads(response.data)

            assert isinstance(data, list)
            prices = [record['price'] for record in data]
            assert all(prices[i] >= prices[i+1] for i in range(len(prices) - 1))

            db.session.delete(b1)
            db.session.delete(b2)
            db.session.commit()

    def test_most_expensive_baked_good_route(self):
        '''has a resource available at "/baked_goods/most_expensive".'''
        response = app.test_client().get('/baked_goods/most_expensive')
        assert response.status_code == 200

    def test_most_expensive_baked_good_route_returns_json(self):
        '''provides a response content type of application/json at "/baked_goods/most_expensive"'''
        response = app.test_client().get('/baked_goods/most_expensive')
        assert response.content_type == 'application/json'

    def test_most_expensive_baked_good_route_returns_one_baked_good_object(self):
        '''returns JSON representing one models.BakedGood object.'''
        with app.app_context():
            prices = [bg.price for bg in BakedGood.query.all()]
            highest_price = max(prices) if prices else 0

            b1 = BakedGood(name="Cake", price=highest_price + 10)
            b2 = BakedGood(name="Cookie", price=highest_price)
            db.session.add_all([b1, b2])
            db.session.commit()

            response = app.test_client().get('/baked_goods/most_expensive')
            data = json.loads(response.data)

            assert isinstance(data, dict)
            assert data['price'] == b1.price

            db.session.delete(b1)
            db.session.delete(b2)
            db.session.commit()
