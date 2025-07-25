#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, date, timedelta
from src.models.billing import db, Client, Billing
from src.main import app

def populate_database():
    with app.app_context():
        # Limpar dados existentes
        db.drop_all()
        db.create_all()
        
        print("🗄️ Criando clientes de teste...")
        
        # Criar clientes de teste
        clients_data = [
            {
                'name': 'João Silva',
                'contact': 'João Silva',
                'email': 'joao.silva@email.com',
                'phone': '(11) 99999-1111'
            },
            {
                'name': 'Maria Santos',
                'contact': 'Maria Santos',
                'email': 'maria.santos@email.com',
                'phone': '(11) 99999-2222'
            },
            {
                'name': 'Pedro Oliveira',
                'contact': 'Pedro Oliveira',
                'email': 'pedro.oliveira@email.com',
                'phone': '(11) 99999-3333'
            },
            {
                'name': 'Ana Costa',
                'contact': 'Ana Costa',
                'email': 'ana.costa@email.com',
                'phone': '(11) 99999-4444'
            },
            {
                'name': 'Carlos Ferreira',
                'contact': 'Carlos Ferreira',
                'email': 'carlos.ferreira@email.com',
                'phone': '(11) 99999-5555'
            }
        ]
        
        clients = []
        for client_data in clients_data:
            client = Client(**client_data)
            db.session.add(client)
            clients.append(client)
        
        db.session.commit()
        print(f"✅ {len(clients)} clientes criados com sucesso!")
        
        print("💰 Criando faturamentos de teste...")
        
        # Criar faturamentos de teste
        today = date.today()
        
        billings_data = [
            # Faturamentos pendentes
            {
                'client_id': clients[0].id,
                'product_service': 'Consultoria em Marketing Digital',
                'price': 1500.00,
                'due_date': today + timedelta(days=15),
                'billing_type': 'unique',
                'payment_status': 'pending'
            },
            {
                'client_id': clients[1].id,
                'product_service': 'Desenvolvimento de Website',
                'price': 3500.00,
                'due_date': today + timedelta(days=30),
                'billing_type': 'unique',
                'payment_status': 'pending'
            },
            {
                'client_id': clients[2].id,
                'product_service': 'Manutenção Mensal de Sistema',
                'price': 800.00,
                'due_date': today + timedelta(days=5),
                'billing_type': 'recurring',
                'payment_status': 'pending',
                'recurring_frequency': 'monthly',
                'recurring_end_date': today + timedelta(days=365)
            },
            
            # Faturamentos pagos
            {
                'client_id': clients[0].id,
                'product_service': 'Criação de Logo',
                'price': 750.00,
                'due_date': today - timedelta(days=10),
                'billing_type': 'unique',
                'payment_status': 'paid'
            },
            {
                'client_id': clients[3].id,
                'product_service': 'Consultoria Jurídica',
                'price': 2200.00,
                'due_date': today - timedelta(days=5),
                'billing_type': 'unique',
                'payment_status': 'paid'
            },
            
            # Faturamentos vencidos
            {
                'client_id': clients[1].id,
                'product_service': 'Suporte Técnico',
                'price': 450.00,
                'due_date': today - timedelta(days=20),
                'billing_type': 'unique',
                'payment_status': 'overdue'
            },
            {
                'client_id': clients[4].id,
                'product_service': 'Treinamento em Excel',
                'price': 600.00,
                'due_date': today - timedelta(days=7),
                'billing_type': 'unique',
                'payment_status': 'overdue'
            },
            
            # Faturamento cancelado
            {
                'client_id': clients[2].id,
                'product_service': 'Projeto de E-commerce',
                'price': 5000.00,
                'due_date': today + timedelta(days=45),
                'billing_type': 'unique',
                'payment_status': 'cancelled'
            },
            
            # Faturamento semanal recorrente
            {
                'client_id': clients[3].id,
                'product_service': 'Limpeza de Escritório',
                'price': 200.00,
                'due_date': today + timedelta(days=7),
                'billing_type': 'recurring',
                'payment_status': 'pending',
                'recurring_frequency': 'weekly',
                'recurring_end_date': today + timedelta(days=180)
            }
        ]
        
        billings = []
        for billing_data in billings_data:
            billing = Billing(**billing_data)
            db.session.add(billing)
            billings.append(billing)
        
        # Criar um faturamento parcelado de exemplo
        installment_billing = Billing(
            client_id=clients[4].id,
            product_service='Sistema de Gestão Empresarial',
            price=12000.00,
            due_date=today + timedelta(days=30),
            billing_type='installment',
            payment_status='pending',
            installment_total=6,
            installment_current=0  # Cobrança pai
        )
        db.session.add(installment_billing)
        db.session.flush()  # Para obter o ID
        
        # Criar as parcelas
        for i in range(6):
            installment_due_date = today + timedelta(days=30 + (i * 30))
            installment = Billing(
                client_id=clients[4].id,
                product_service=f'Sistema de Gestão Empresarial - Parcela {i+1}/6',
                price=2000.00,
                due_date=installment_due_date,
                billing_type='installment',
                payment_status='pending' if i > 0 else 'paid',  # Primeira parcela paga
                installment_total=6,
                installment_current=i+1,
                installment_parent_id=installment_billing.id
            )
            db.session.add(installment)
            billings.append(installment)
        
        db.session.commit()
        print(f"✅ {len(billings) + 7} faturamentos criados com sucesso!")  # +7 pelas parcelas
        
        print("\n📊 Resumo dos dados criados:")
        print(f"👥 Clientes: {len(clients)}")
        print(f"💰 Faturamentos: {len(billings) + 7}")
        print(f"📅 Tipos: Únicos, Recorrentes (semanal/mensal), Parcelados")
        print(f"📈 Status: Pendentes, Pagos, Vencidos, Cancelados")
        print("\n✅ Banco de dados populado com sucesso!")
        print("🚀 O sistema está pronto para uso!")

if __name__ == '__main__':
    populate_database()

