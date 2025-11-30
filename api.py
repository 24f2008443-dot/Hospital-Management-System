from flask import Blueprint
from flask_restful import Resource, Api, reqparse
from models import Doctor, Availability
from datetime import date, timedelta

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class DoctorList(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str, location='args')
        parser.add_argument('page', type=int, location='args', default=1)
        parser.add_argument('per_page', type=int, location='args', default=10)
        args = parser.parse_args()

        q = args['q']
        page = args['page']
        per_page = args['per_page']

        query = Doctor.query.filter(Doctor.is_blacklisted == False)
        if q:
            like = f"%{q}%"
            query = query.filter((Doctor.fullname.ilike(like)) | (Doctor.specialization.ilike(like)))

        pagination = query.order_by(Doctor.fullname).paginate(page=page, per_page=per_page, error_out=False)
        items = []
        for d in pagination.items:
            items.append({
                'id': d.id,
                'fullname': d.fullname,
                'specialization': d.specialization,
                'department': d.department.name if d.department else None
            })
        return {
            'doctors': items,
            'page': page,
            'per_page': per_page,
            'total': pagination.total
        }

class DoctorAvailability(Resource):
    def get(self, doctor_id):
        today = date.today()
        end = today + timedelta(days=7)
        avail_q = Availability.query.filter(
            Availability.doctor_id == doctor_id,
            Availability.date >= today,
            Availability.date <= end
        ).order_by(Availability.date).all()
        data = []
        for a in avail_q:
            data.append({
                'date': a.date.isoformat(),
                'start_time': a.start_time.strftime('%H:%M'),
                'end_time': a.end_time.strftime('%H:%M')
            })
        return { 'availability': data }

api.add_resource(DoctorList, '/api/doctors')
api.add_resource(DoctorAvailability, '/api/doctors/<int:doctor_id>/availability')
