from flask import Blueprint, request, jsonify
from pdhs_app.models.users.user import User  # 
from pdhs_app.models.comments.comment import Comment

bp = Blueprint('comments', __name__, url_prefix='/comments')


@bp.route('/hello', methods=['GET'])
def hello():
    if request.method == 'GET':
        return "Hello from /comment"

@bp.route('/', methods=['GET'])
def get_all_comments():
    """
    Get all the comments in the comment
    table.
    """
    if request.method == 'GET':
        comments = []
        result = []
        error_msg = None
        try:
            result = Comment.query.all()
        except:
            error_msg = 'Error occured retrieving comments'
        if len(result) == 0:
            error_msg = 'No comments available'
        if error_msg is not None:
            return jsonify(msg=error_msg)
        else:
            for comment in result:
                comments.append(comment.to_json())
            return jsonify(comments=comments)


@bp.route('/<int:comment_id>', methods=['GET'])
def get_comment_by_id(comment_id):
    """
    Get a particular comment by id
    """
    if request.method == 'GET':
        error_msg = None
        try:
            comment = Comment.find_by_id(comment_id)
            if comment is None:
                error_msg = f'No comment with ID {comment_id} found'
        except:
            error_msg = 'Error occured finding comment'
        if error_msg is not None:
            return jsonify(msg=error_msg), 404
        elif comment is not None:
            return jsonify(comment.to_json())


@bp.route('/create', methods=['POST'])
def create_comment():
    """
    Create a comment
    """
    if request.method == 'POST':
        content = request.json.get('content', None)
        sender_id = request.json.get('sender_id', None)
        document_id = request.json.get('document_id', None)
        error_msg = None
        if not content:
            error_msg = 'content is required.'
        elif not sender_id:
            error_msg = 'Recipient ID is required.'
        elif not document_id:
            error_msg = 'Document ID is required.'
        if error_msg is not None:
            return jsonify(msg=error_msg), 500
        else:
            new_comment = Comment(
                content=content,
                document_id=document_id,
                sender_id=sender_id
            )
            try:
                new_comment.save_to_db()
            except:
                return jsonify(msg='Error saving Comment to database'), 500
            return jsonify(new_comment.to_json()), 201



@bp.route('/delete/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    if request.method == 'DELETE':
        try:
            comment = Comment.find_by_id(comment_id)
        except:
            return jsonify(msg='Error occured finding comment'), 404
        if comment is not None:
            try:
                comment.delete_from_db()
            except:
                return jsonify(msg='Error occured deleting Comment'), 500
        else:
            return jsonify(msg='Comment does not exist.'), 404
        return jsonify(msg='Comment deleted successfully'), 200
