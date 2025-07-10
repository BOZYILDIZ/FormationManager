from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db, log_user_action
from app.models import Client, Formation, Product
from app.utils.decorators import admin_required
from datetime import datetime

client_bp = Blueprint('client', __name__, url_prefix='/client')

@client_bp.route('/<int:client_id>')
@login_required
def client_detail(client_id):
    client = Client.query.get_or_404(client_id)
    products = Product.query.filter_by(client_id=client_id).all()
    
    # Calculer le total des produits
    total_products = sum(product.price for product in products)
    
    # Calculer le montant restant à utiliser
    remaining = client.bon_value - total_products
    
    # Calculer le pourcentage d'utilisation
    usage_percent = (total_products / client.bon_value * 100) if client.bon_value > 0 else 0
    
    log_user_action(f"A consulté les détails du client ID:{client_id} ({client.name})")
    
    return render_template('client/detail.html', 
                          client=client, 
                          products=products,
                          total_products=total_products,
                          remaining=remaining,
                          usage_percent=usage_percent)

@client_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_client():
    formations = Formation.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        formation_id = request.form.get('formation_id')
        cpf_id = request.form.get('cpf_id')
        
        if not name or not email or not formation_id:
            flash('Veuillez remplir tous les champs obligatoires', 'danger')
            return render_template('client/create.html', formations=formations)
        
        # Vérifier si le client existe déjà
        existing_client = Client.query.filter_by(email=email).first()
        if existing_client:
            flash('Un client avec cet email existe déjà', 'danger')
            return render_template('client/create.html', formations=formations)
        
        # Créer le client
        client = Client(
            name=name,
            email=email,
            phone=phone,
            formation_id=formation_id,
            cpf_id=cpf_id
        )
        
        # Calculer la valeur du bon d'achat
        client.update_bon_value()
        
        db.session.add(client)
        db.session.commit()
        
        log_user_action(f"A créé un nouveau client: {name} (ID:{client.id})")
        flash('Client créé avec succès', 'success')
        return redirect(url_for('client.client_detail', client_id=client.id))
    
    return render_template('client/create.html', formations=formations)

@client_bp.route('/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    formations = Formation.query.all()
    
    if request.method == 'POST':
        old_name = client.name
        old_email = client.email
        old_formation_id = client.formation_id
        
        client.name = request.form.get('name')
        client.email = request.form.get('email')
        client.phone = request.form.get('phone')
        client.cpf_id = request.form.get('cpf_id')
        
        # Mettre à jour la formation si elle a changé
        new_formation_id = int(request.form.get('formation_id'))
        if client.formation_id != new_formation_id:
            client.formation_id = new_formation_id
            client.update_bon_value()
        
        # Mettre à jour le type de bon (fixe ou pourcentage)
        bon_type = request.form.get('bon_type')
        if bon_type == 'fixed':
            client.fixed_bon_value = float(request.form.get('fixed_bon_value', 0))
            client.bon_percentage = None
        else:
            client.bon_percentage = float(request.form.get('bon_percentage', 0))
            client.fixed_bon_value = None
        
        # Recalculer la valeur du bon
        client.update_bon_value()
        
        # Mettre à jour le statut de paiement
        client.payment_received = 'payment_received' in request.form
        
        # Mettre à jour la date de facturation
        invoice_date = request.form.get('invoice_date')
        if invoice_date:
            client.invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d')
            client.update_expected_payment_date()
        else:
            client.invoice_date = None
            client.expected_payment_date = None
        
        db.session.commit()
        
        # Journaliser les changements importants
        changes = []
        if old_name != client.name:
            changes.append(f"nom: {old_name} -> {client.name}")
        if old_email != client.email:
            changes.append(f"email: {old_email} -> {client.email}")
        if old_formation_id != client.formation_id:
            old_formation = Formation.query.get(old_formation_id)
            new_formation = Formation.query.get(client.formation_id)
            changes.append(f"formation: {old_formation.title if old_formation else 'Aucune'} -> {new_formation.title if new_formation else 'Aucune'}")
        
        if changes:
            log_user_action(f"A modifié le client ID:{client_id} - {', '.join(changes)}")
        
        flash('Client mis à jour avec succès', 'success')
        return redirect(url_for('client.client_detail', client_id=client.id))
    
    return render_template('client/edit.html', client=client, formations=formations)

@client_bp.route('/<int:client_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    
    db.session.delete(client)
    db.session.commit()
    
    flash('Client supprimé avec succès', 'success')
    return redirect(url_for('main.dashboard'))

# Routes pour les produits
@client_bp.route('/<int:client_id>/add-product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product(client_id):
    client = Client.query.get_or_404(client_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price', 0))
        url = request.form.get('url')
        delivered = 'delivered' in request.form
        
        if not name or price <= 0:
            flash('Veuillez remplir tous les champs obligatoires', 'danger')
            return redirect(url_for('client.add_product', client_id=client_id))
        
        product = Product(
            client_id=client_id,
            name=name,
            price=price,
            url=url,
            delivered=delivered
        )
        
        db.session.add(product)
        db.session.commit()
        
        log_user_action(f"A ajouté un produit '{name}' ({price}€) pour le client ID:{client_id}")
        flash('Produit ajouté avec succès', 'success')
        return redirect(url_for('client.client_detail', client_id=client_id))
    
    return render_template('client/add_product.html', client=client)

@client_bp.route('/product/<int:product_id>/toggle-delivered', methods=['POST'])
@login_required
@admin_required
def toggle_product_delivered(product_id):
    product = Product.query.get_or_404(product_id)
    product.delivered = not product.delivered
    db.session.commit()
    
    status = "livré" if product.delivered else "non livré"
    log_user_action(f"A marqué le produit ID:{product_id} comme {status} pour le client ID:{product.client_id}")
    
    return jsonify(success=True, delivered=product.delivered)

@client_bp.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    client_id = product.client_id
    product_name = product.name
    
    db.session.delete(product)
    db.session.commit()
    
    log_user_action(f"A supprimé le produit '{product_name}' (ID:{product_id}) du client ID:{client_id}")
    flash('Produit supprimé avec succès', 'success')
    
    return redirect(url_for('client.client_detail', client_id=client_id)) 