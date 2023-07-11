from flask import Blueprint, request, jsonify, render_template
from pdhs_app.models.users.user import User  
from pdhs_app.models.portfolios.portfolio import Portfolio

bp = Blueprint('portfolios', __name__, url_prefix='/portfolios')


@bp.route('/', methods=['GET'])
def all():
    error_msg = None
    try:
        portfolios = Portfolio.query.all()
    except:
        error_msg = 'Error occured retrieving portfolios'
    if portfolios is None:
        error_msg = 'No portfolios available'
    if error_msg is not None:
        return jsonify(msg=error_msg), 404
    result = [portfolio.to_json() for portfolio in portfolios]
    return jsonify(portfolios=result), 200


@bp.route('/<int:portfolio_id>', methods=['GET'])
def get_portfolio_by_id(portfolio_id):
    """
    Get a particular portfolio by id
    """
    if request.method == 'GET':
        error_msg = None
        try:
            portfolio = Portfolio.find_by_id(portfolio_id)
        except:
            error_msg = 'Error occured finding portfolio'
        if error_msg is not None:
            return jsonify(msg=error_msg), 404
        elif portfolio is not None:
            return jsonify(portfolio.to_json()), 200


@bp.route('/new', methods=['POST', 'GET'])
def create_portfolio():
    """
    Create a portfolio
    """
    if request.method == 'POST':
        _id = request.form['id'] if request.form['id'] else request.json.get('id', None) 
        name = request.form['name'] if request.form['name'] else request.json.get('name', None)
        
        error_msg = None
        if not id:
            error_msg = 'Id is required.'
        elif not name:
            error_msg = 'Name is required.'
        if error_msg is not None:
            return jsonify(msg=error_msg), 500
        else:
            new_portfolio = Portfolio(id=_id, name=name)
            try:
                new_portfolio.save_to_db()
            except:
                return jsonify(msg='Error saving Portfolio to database'), 500
            return jsonify(new_portfolio.to_json()), 201
    return render_template("portfolios/add_portfolio.html")


@bp.route('/update/<int:portfolio_id>', methods=['PUT'])
def update_portfolio(portfolio_id):
    """
    Update a Portfolio
    """
    if request.method == 'PUT':
        name = request.json.get('name', None)
        can_approve = request.json.get('can_approve', None)
        is_student = request.json.get('is_student', None)

        if not portfolio_id:
            return jsonify(msg='Id is required.'), 500
        else:
            try:
                new_portfolio = Portfolio.find_by_id(portfolio_id)
                if new_portfolio is not None:
                    if name is not None:
                        new_portfolio.name = name
                    new_portfolio.can_approve = bool(can_approve)
                    new_portfolio.is_student = bool(is_student)
                    new_portfolio.save_to_db()
            except:
                return jsonify(msg='Error updating Portfolio'), 500
            return jsonify(new_portfolio.to_json()), 201


@bp.route('/delete/<int:portfolio_id>', methods=['DELETE'])
def delete_portfolio(portfolio_id):
    if request.method == 'DELETE':
        error_msg = None
        try:
            portfolio = Portfolio.find_by_id(portfolio_id)
        except:
            error_msg = 'Error occured finding portfolio'
        if portfolio is not None:
            try:
                portfolio.delete_from_db()
            except:
                error_msg = 'Error occured deleting Portfolio'
        if error_msg is not None:
            return jsonify(msg=error_msg), 404
        else:
            return jsonify(msg='Portfolio deleted successfully'), 200
