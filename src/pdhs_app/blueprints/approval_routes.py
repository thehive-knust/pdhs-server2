from flask import Blueprint, request, jsonify
from pdhs_app.models.users.user import User  # 
from pdhs_app.models.approvals.approval import Approval
from pdhs_app.models.approvals import errors as ApprovalErrors
from pdhs_app.models.documents.document import Document
from datetime import datetime

bp = Blueprint('approvals', __name__, url_prefix='/approvals')


@bp.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        result = request.get_json()
        doc_id = result['doc_id']
        recipient_id = result['user_id']
        status = result['status']
        try:
            approval = Approval.query.filter_by(document_id=doc_id, recipient_id=recipient_id).first()
        except:
            print("================================= Approval try exited")
            return jsonify(message="Error updating approval")
        
        try:
            doc = Document.find_by_id(id=doc_id)
        except:
            print("================================= Doc try exited")
            return jsonify(message=f"Error updating document {doc_id}")
        
        if status == "rejected":
            doc.progress = status
            print("====================== Printed Status ===================", doc.to_json())
            
        print("===============Before: Approval JSON==============", approval.to_json())
        approval.status = status
        print("===============After: Approval JSON==============", approval.to_json())
        approval.save_to_db() 
        
        try:
            recipient_list = Approval.query.filter_by(document_id=doc_id)
        except:
            return jsonify(message=f"Error getting recipients for document {doc_id}")

        if recipient_list:
            rlist = [j for j in recipient_list]
            i = len(rlist) - 1
            for recipient in recipient_list:
                    if recipient.status == "approved" and i > 0:
                        print(">>>>>>>>>>> Was in A when i was ", i)
                        i = i - 1
                    elif recipient.status == "approved" and i == 0:
                        doc.progress = recipient.status
                        print(">>>>>>>>>>> Was in B when i was ", i)
                    else:
                        break
                                       
        doc.updated_at = datetime.utcnow()
        doc.save_to_db()
        
        return {"message": "Done"}


@bp.route('/', methods=['GET'])
def get_all_approvals():
    """
    Get all the approvals in the approval
    table.
    """
    if request.method == 'GET':
        approvals = []
        result = []
        error_msg = None
        try:
            result = Approval.query.all()
        except:
            error_msg = 'Error occured retrieving approvals'
        if len(result) == 0:
            error_msg = 'No approvals available'
        if error_msg is not None:
            return jsonify(msg=error_msg)
        else:
            for approval in result:
                approvals.append(approval.to_json())
            return jsonify(approvals=approvals)


@bp.route('/<int:approval_id>', methods=['GET'])
def get_approval_by_id(approval_id):
    """
    Get a particular approval by id
    """
    if request.method == 'GET':
        error_msg = None
        try:
            approval = Approval.find_by_id(approval_id)
            if approval is None:
                error_msg = f'No approval with ID {approval_id} found'
        except:
            error_msg = 'Error occured finding approval'
        if error_msg is not None:
            return jsonify(msg=error_msg), 404
        elif approval is not None:
            return jsonify(approval.to_json())

@bp.route('/delete/<int:approval_id>', methods=['DELETE'])
def delete_approval(approval_id):
    if request.method == 'DELETE':
        error_msg = None
        try:
            approval = Approval.find_by_id(approval_id)
        except:
             error_msg = 'Error occured finding approval'
        if approval is not None:
            try:
                approval.delete_from_db()
            except:
                error_msg = 'Error occured deleting Approval'
        if error_msg is not None:
            return jsonify(msg=error_msg), 404
        else:
            return jsonify(msg='Approval deleted successfully')
