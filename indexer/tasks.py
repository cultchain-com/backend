from celery import shared_task
from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_parser.models import *
from django.utils import timezone
from django.db import transaction
from datetime import datetime
from .utils import *


@shared_task
def process_all_events():
    print("Its processing....")
    get_proposals()
    update_proposal_status()
    get_milestones()
    update_milestone_status()
    update_milestone_data()
    handle_committee_formed()
    handle_chosen_as_committee_member()
    handle_decision_recorded_event()
    handle_final_decision_event()
    handle_donated_to_event_event()