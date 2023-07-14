from flask import Blueprint, request, jsonify, current_app, render_template
from pdhs_app.models.users.user import User  # 
from pdhs_app.models.documents.document import Document
from pdhs_app.models.approvals.approval import Approval
from pdhs_app.models.portfolios.portfolio import Portfolio
from werkzeug.utils import secure_filename
# from storage.cloud_storage import delete_blob, upload_blob    # This was used for google cloud services
from middleware.cloud_upload import upload_file     # This is being used for cloudinary sevices
import os, json

bp = Blueprint('documents', __name__, url_prefix='/documents')


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def _allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/test', methods=['GET', 'POST'])
def test():
    apvs = Approval.query.all()
    for e in apvs:
        e.delete_from_db()
    documents = Document.query.all()
    for doc in documents:
        doc.delete_from_db()
    return jsonify(msg="Done")


@bp.route('/', methods=['GET'])
def get_all_docs():
    """
    Return all the documents in the document table
    """
    if request.method == 'GET':
        result = []
        documents = []
        try:
            result = Document.query.all()
        except:
            return jsonify({'msg': 'There was an error retrieving the items requested'}), 500
        for doc in result:
            documents.append(doc.to_json())
        if len(documents) == 0 or len(result) == 0:
            return jsonify({'msg': 'There are no uploaded documents'}), 404
        return jsonify({'documents': documents})


@bp.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        request_data = request.form.to_dict()
        doc_subject = request_data.get('subject', None)
        doc_description = request_data.get('description', None)
        user_id = request_data.get('user_id', None) 
        doc_file = request.files.get('file', None)
        print("==========================================PRINTING DATA======================================")
        print("======================DOC FILE====================", doc_file)
        print("========================DATES==================", request.files.get('createdAt', None), request.files.get('updatedAt', None))
        
        # Handling the creation of a new document object
        error_msg = None
            
        if doc_subject is None:
            error_msg = 'Document subject is required'
            
        elif doc_description is None:
            error_msg = 'Document description is required'
            
        elif user_id is None:
            error_msg = 'User ID is required'
            
        if doc_file is None:
            error_msg = 'No selected file'
            
        if error_msg is not None:
            return jsonify(msg=error_msg), 500
        else:
            new_document = Document(
                subject=doc_subject,
                user_id=user_id,
                description=doc_description #name , file
            )   
        doc_id= None
        if _allowed_file(doc_file.filename):
                filename = secure_filename(doc_file.filename)
                new_document.name = filename
                try:
                    document_url = upload_file(doc_file) #upload_blob(doc_file.stream, filename)
                    print('>>>>>>>> document_url', document_url)
                    if document_url['msg'] is not None:
                        raise Exception("Error exception.")
                    else:
                        new_document.file = document_url
                except Exception as e:
                    print('>>>>>>>> Error uploading file: %s' % e)
                    return jsonify(msg='Error saving document'), 500
                try:
                    doc_id = new_document.save_to_db()
                except:
                    print('>>>>>>>> WAS HERE (~)')
                    return jsonify(msg='Error saving document'), 500
        else:
            return jsonify(msg="File type not supported"), 201

        # Handling the associated people to approve the document
        result = json.loads(request_data['recipients'])
        print("===========================RECIPIENTS============================", result, type(result))
        recipients = result.keys()
        print("===========================KEYS============================", recipients)
        for recipient in recipients:
            new_approval = Approval(document_id=doc_id, recipient_id=recipient).save_to_db()
        return jsonify(message="Done!")
    return render_template("documents/upload_document.html")
                

@bp.route('/new/<int:user_id>', methods=['GET'])
def inbox(user_id):
    if request.method == 'GET':
        recieved_documents = []
        error_msg = None
        try:
            result = Approval.query.filter_by(recipient_id=user_id)
        except:
            error_msg = 'Error occured retrieving recieved documents'
            
        if error_msg is not None:
            return jsonify(msg=error_msg)
        
        documents = []
        if result:
            for approval in result:
                if approval.status == "pending":
                    recipient_list = Approval.query.filter_by(document_id=approval.document_id)
                    for recipient in recipient_list:
                        print("================= Recipient Associated with a doc", recipient.recipient_id)
                        if recipient.status == "approved" and recipient.recipient_id != user_id :
                            continue
                        elif recipient.status == "rejected" and recipient.recipient_id != user_id :
                            break
                        elif recipient.status == "pending" and recipient.recipient_id != user_id :
                            break
                        elif recipient.status == "pending" and recipient.recipient_id == user_id:
                            doc = Document.find_by_id(id=recipient.document_id) 
                            documents.append(doc)
                else:
                    doc = Document.find_by_id(id=approval.document_id) 
                    doc.progress = approval.status
                    documents.append(doc)
            
#             documents = [ Document.find_by_id(id=elem.document_id) for elem in result ]
            if documents:
                for document in documents:
                    sender = User.find_by_id(document.user_id).to_json()
                    sender_name = sender['first_name'] + " " + sender['last_name']
                    sender_title = sender['portfolio']
                    sender_contact = sender['contact']
                    sender_img_url = sender['img_url']
                    doc = document.to_json()
                    doc['user_info'] = {'name':sender_name, 'title':sender_title, 'contact':sender_contact, 'img_url':sender_img_url}
                    recieved_documents.append(doc) 
        print("=========================INBOX Documents===============================", recieved_documents)
        return jsonify({'documents': recieved_documents}) 
    

@bp.route('/approved/<int:user_id>', methods=['GET'])
def approved(user_id):
    if request.method == 'GET':
        approved_documents = Approval.query.filter_by(recipient_id=user_id, status="Approved")
        return jsonify(approved_documents)  

@bp.route('/rejected/<int:user_id>', methods=['GET'])
def rejected(user_id):
    if request.method == 'GET':
        rejected_documents = Approval.query.filter_by(recipient_id=user_id, status="Rejected")
        return jsonify(rejected_documents)        
        
@bp.route('/cancel', methods=['GET'])
def cancel():
    if request.method == 'GET':
        result = request.get_json()
        document_id = result['document_id']
        all_approvals = Approval.query.filter_by(document_id=document_id)
        for approval in all_approvals:
            approval.delete_from_db()
        Document.query.filter_by(id=document_id).delete_from_db()
        return {"message": "Done"}


@bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_documents(user_id):
    """
    Get all the documents created or 
    uploaded by a particular user.
    """
    if request.method == 'GET':
        user_documents = []
        error_msg = None
        try:
            documents = Document.query.filter_by(user_id=user_id)
        except:
            error_msg = 'Error occured retrieving user documents'
            
        if error_msg is not None:
            return jsonify(msg=error_msg)
        
        for document in documents:
            doc_approvals = Approval.query.filter_by(document_id=document.id)
            recipients = []
            statuses = []
            for approval in doc_approvals:
                recipient = User.find_by_id(approval.recipient_id)
                recipient_portfolio = Portfolio.find_by_id(recipient.portfolio_id) 
                department_id = f"({recipient.department_id})" if recipient.department_id else " "
                recipients.append(recipient_portfolio.name + department_id)
                statuses.append(approval.status)
            document.approval_list = dict(zip(recipients, statuses))
            user_documents.append(document.to_json())
        print("=========================Sent Documents===============================", user_documents)
        return jsonify(documents=user_documents)


@bp.route('/<int:document_id>', methods=['GET'])
def get_document_by_id(document_id):
    """
    Get a particular document by id
    """
    if request.method == 'GET':
        document = None
        error_msg = None
        try:
            document = Document.find_by_id(document_id)
        except:
            error_msg = 'Error occured finding document'
        if error_msg is not None:
            return jsonify(msg=error_msg)
        elif document is not None:
            return jsonify(document.to_json())

@bp.route('/delete/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    if request.method == 'DELETE':
        error_msg = None
        try:
            document = Document.find_by_id(document_id)
        except:
            error_msg = 'Error occured finding document'
            return jsonify(msg=error_msg), 404
        if document is not None:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>ABOUT TO DELETE", document)
            try:
                approvals = Approval.query.filter_by(document_id=document.id)
            except:
                error_msg = 'Error occured getting Document approvals from database.'
                return jsonify(msg=error_msg), 404
            if approvals is not None:
                for approval in approvals:
                    approval.delete_from_db()
#             try:
#                 delete_blob(document.file)
#             except:
#                 error_msg = 'Error occured deleting Document from cloud.'
#                 return jsonify(msg=error_msg), 404
            try:
                document.delete_from_db()
            except:
                error_msg = 'Error occured deleting Document from database.'
                return jsonify(msg=error_msg), 404
#         if error_msg is not None:
#             return jsonify(msg=error_msg), 404
#         else:
            return jsonify(msg='Document deleted successfully')
