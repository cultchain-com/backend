from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_parser.models import *
from user_profile.models import *
from .models import *
from django.utils import timezone
from .contract_enums import *
from decimal import Decimal
import datetime


def handle_applied_as_validator_event():
    contract_obj = Contract.objects.get(contract_name="Validator")

    # Set up web3 and contract
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    applied_as_validator_events = contract.events.AppliedAsValidator().get_logs(
        fromBlock=contract_obj.last_processed_event_block,
        toBlock="latest"
    )

    for event in applied_as_validator_events:

        applicant_address = event['args']['applicant']
        ipfs_hash = event['args']['_ipfsHash']
        committee_id = event['args']['committeeId']
        status = event['args']['status']

        # Fetch or create the user profile
        user_profile, _ = UserProfile.objects.get_or_create(wallet_address=applicant_address)

        # Create or update the validator request
        ValidatorRequest.objects.update_or_create(
            applicant=user_profile,
            defaults={
                'ipfs_hash': ipfs_hash,
                'validation_status': status,
                'committee_id': committee_id
            }
        )


def handle_validator_request_responded_event():
    contract_obj = Contract.objects.get(contract_name="Validator")

    # Set up web3 and contract
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    validator_request_responded_events = contract.events.ValidatorRequestResponded().get_logs(
        fromBlock=contract_obj.last_processed_event_block,
        toBlock="latest"
    )

    for event in validator_request_responded_events:
        applicant_address = event['args']['applicant']
        status = event['args']['status']

        # Fetch the user profile
        user_profile = UserProfile.objects.get(wallet_address=applicant_address)

        # Update the validator request status
        validator_request = ValidatorRequest.objects.get(applicant=user_profile)
        validator_request.validation_status = status
        validator_request.save()


def handle_final_decision_event():
    contract_obj = Contract.objects.get(contract_name="RandomizedCommittee")

    # Set up web3 and contract
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    final_decision_events = contract.events.FinalDecision().get_logs(
        fromBlock=contract_obj.last_processed_event_block,
        toBlock="latest"
    )
    print(f"Final Decision logs: {final_decision_events}")
    for event in final_decision_events:
        committee_id = event['args']['committeeId']
        decision = event['args']['finalDecision']

        committee_instance = Committee.objects.get(committee_id=committee_id)
        committee_instance.final_decision = decision

        committee_instance.save()


def handle_decision_recorded_event():
    contract_obj = Contract.objects.get(contract_name="RandomizedCommittee")

    # Set up web3 and contract
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    decision_recorded_events = contract.events.DecisionRecorded().get_logs(
        fromBlock=contract_obj.last_processed_event_block,
        toBlock="latest"
    )

    for event in decision_recorded_events:
        committee_id = event['args']['committeeId']
        member = event['args']['member']
        decision = event['args']['decision']
        feedback = event['args']['feedback']

        member_profile, _ = UserProfile.objects.get_or_create(wallet_address=member)
        committee_instance = Committee.objects.get(committee_id=committee_id)

        committee_membership = CommitteeMembership.objects.get(committee=committee_instance, member=member_profile)

        if not committee_membership.has_voted:
            committee_membership.has_voted = True
            committee_membership.decision = decision
            committee_membership.feedback = feedback
            committee_membership.save()

            if decision:
                committee_instance.yes_votes += 1
            else:
                committee_instance.no_votes += 1
            committee_instance.save()


def handle_chosen_as_committee_member():
    contract_obj = Contract.objects.get(contract_name="RandomizedCommittee")

    # Set up web3 and contract
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    chosen_member_events = contract.events.ChosenAsCommitteeMember().get_logs(
        fromBlock=contract_obj.last_processed_event_block,
        toBlock="latest"
    )

    for event in chosen_member_events:
        committee_id = event['args']['newCommitteeId']
        committee_type_id = event['args']['_committeeTypeId']
        milestone_index = event['args']['_milestoneIndex']
        committee_type = CommitteeType(
            event['args']['_committeeType']).name  # Assuming CommitteeType is an Enum in your Django code
        member_address = event['args']['member']

        # Fetch the committee instance
        committee_instance, _ = Committee.objects.get_or_create(committee_id=committee_id)

        # Logic to add/update each member's detailed information
        user_profile, _ = UserProfile.objects.get_or_create(wallet_address=member_address)
        committee_member, _ = CommitteeMembership.objects.get_or_create(member=user_profile, committee=committee_instance)
        committee_member.committee_type = committee_type
        committee_member.committee_type_id = committee_type_id
        committee_member.milestone_index = milestone_index
        committee_member.save()

        # Add the member to the committee if not already added
        if committee_member not in committee_instance.members.all():
            committee_instance.members.add(committee_member.member)

    # Update the last processed block
    contract_obj.save()


def handle_committee_formed():
    contract_obj = Contract.objects.get(contract_name="RandomizedCommittee")

    # Set up web3 and contract
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    committee_formed_events = contract.events.CommitteeFormed().get_logs(
        fromBlock=contract_obj.last_processed_event_block,
        toBlock="latest"
    )

    for event in committee_formed_events:
        committee_id = event['args']['committeeId']
        members = event['args']['members']
        committee_type_id = event['args']['_committeeTypeId']
        milestone_index = event['args']['_milestoneIndex']
        committee_type = CommitteeType(
            event['args']['_committeeType']).name

        committee_instance, created = Committee.objects.get_or_create(
            committee_id=committee_id,
            defaults={
                'final_decision': None,  # or set a default if needed
                'total_members': len(members),
                'committee_type': committee_type,
                'committee_type_id': committee_type_id,
                'milestone_index': milestone_index
            }
        )

        if created:
            # Assuming you have a related model for members (e.g., CommitteeMember)
            for member_address in members:
                user_profile, _ = UserProfile.objects.get_or_create(wallet_address=member_address)
                committee_member, _ = CommitteeMembership.objects.get_or_create(member=user_profile, committee=committee_instance)
                committee_instance.members.add(user_profile)

            committee_instance.save()

    contract_obj.save()


def update_proposal_status():
    contract_obj = Contract.objects.get(contract_name="CharityEvent")
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    # Fetch the ProposalStatusUpdated events
    proposal_status_updated_events = contract.events.ProposalStatusUpdated().get_logs(
        fromBlock=contract_obj.last_processed_event_block,
        toBlock="latest"
    )

    for event in proposal_status_updated_events:
        event_id = event['args']['eventId']
        status = EventMilestoneStatus(event['args']['status']).name  # Convert to string representation

        # Update the event in the database
        try:
            charity_event = Event.objects.get(id=event_id)
            charity_event.status = status
            charity_event.save()

        except Event.DoesNotExist:
            print("Event don't exist: ", event_id)
            pass


def convert_timestamp_to_datetime(endDate):
    # If the timestamp is larger than a certain threshold (e.g., year 3000 in seconds),
    # assume it's in milliseconds and divide by 1000
    if endDate > 32503680000:
        endDate /= 1000
    return timezone.datetime.fromtimestamp(endDate, tz=timezone.utc)


def get_proposals():
    contract_obj = Contract.objects.get(contract_name="CharityEvent")
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    propasal_creation_event = contract.events.ProposalCreated().get_logs(fromBlock=contract_obj.last_processed_event_block, toBlock="latest")

    for event in propasal_creation_event:
        event_id = event['args']['eventId']
        creator = event['args']['creator']
        event_name = event['args']['name']
        event_description = event['args']['description']
        target_amount = Decimal(event['args']['targetAmount'])
        collected_amount = Decimal(event['args']['collectedAmount'])
        endDate = event['args']['endDate']
        category = event['args']['category']
        committeeId = event['args']['committeeId']
        isFundraisingOver = event['args']['isFundraisingOver']
        block_number = event['blockNumber']
        timestamp = web3.eth.get_block(block_number)["timestamp"]
        tokenUri = contract.functions.tokenURI(event_id).call()

        # Now Save it
        user_profile, _ = UserProfile.objects.get_or_create(wallet_address=creator)

        created_at = timezone.datetime.fromtimestamp(timestamp, tz=timezone.utc)
        event_date = convert_timestamp_to_datetime(endDate)
        print(f"End Date Datetime: {event_date}")
        try:
            event_instance, created = Event.objects.get_or_create(
                id=event_id,
                defaults={
                    'creator': user_profile,
                    'name': event_name,
                    'description': event_description,
                    'target_amount': target_amount,
                    'collected_amount': collected_amount,
                    'end_date': event_date,
                    'created_at': created_at,
                    'category': EventCategory(category).name,
                    'status': EventMilestoneStatus(0).name,
                    'rating_sum': 0,
                    'rating_count': 0,
                    'committee_id': committeeId,
                    'is_fundraising_over': isFundraisingOver,
                    'token_uri': tokenUri
                }
            )
            event_instance.save()

        except Exception as e:
            print(f"EXCEPTION: {e}")


def update_milestone_data():
    contract_obj = Contract.objects.get(contract_name="CharityEvent")
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    # Fetch the MilestoneMarkedAsCompleted events
    milestone_completed_events = contract.events.MilestoneMarkedAsCompleted().get_logs(
        fromBlock=contract_obj.last_processed_event_block,
        toBlock="latest"
    )

    for event in milestone_completed_events:
        event_id = event['args']['eventId']
        milestone_index = event['args']['milestoneIndex']
        spended_amount = Decimal(event['args']['spendedAmount'])

        # Update the milestone in the database
        try:
            charity_event = Event.objects.get(id=event_id)
            milestone = Milestone.objects.get(event=charity_event, milestone_index=milestone_index)
            milestone.spended_amount = spended_amount
            milestone.completed = True
            milestone.save()

        except (Event.DoesNotExist, IndexError):
            print(f"Event with ID {event_id} doesn't exist or milestone index {milestone_index} is out of range.")
            pass


def update_milestone_status():
    contract_obj = Contract.objects.get(contract_name="CharityEvent")
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    # Fetch the MilestoneStatusUpdated events
    milestone_status_updated_events = contract.events.MilestoneStatusUpdated().get_logs(
        fromBlock=contract_obj.last_processed_event_block,
        toBlock="latest"
    )

    for event in milestone_status_updated_events:
        event_id = event['args']['eventId']
        milestone_index = event['args']['milestoneIndex']
        decision = event['args']['decision']
        is_completed = event['args']['_iscomplited']

        # Determine the status based on the decision and is_completed values
        if is_completed:
            status = EventMilestoneStatus.Approved.name if decision else EventMilestoneStatus.Rejected.name
        else:
            status = EventMilestoneStatus.Pending.name

        # Update the milestone in the database
        try:
            charity_event = Event.objects.get(id=event_id)
            milestone = Milestone.objects.get(event=charity_event, milestone_index=milestone_index)
            milestone.status = status
            milestone.completed = is_completed
            milestone.save()

        except (Event.DoesNotExist, IndexError):
            print(f"Event with ID {event_id} doesn't exist or milestone index {milestone_index} is out of range.")
            pass


def get_milestones():
    contract_obj = Contract.objects.get(contract_name="CharityEvent")
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    milestone_creation_event = contract.events.MilestoneCreated().get_logs(fromBlock=contract_obj.last_processed_event_block, toBlock="latest")

    for event in milestone_creation_event:
        event_id = event['args']['eventId']
        milestone_index = event['args']['milestoneIndex']
        milestone_name = event['args']['milestoneName']
        description = event['args']['description']
        target_amount = Decimal(event['args']['targetAmount'])
        endDate = event['args']['endDate']
        status = EventMilestoneStatus(event['args']['status']).name
        block_number = event['blockNumber']
        timestamp = web3.eth.get_block(block_number)["timestamp"]

        # Convert the timestamp to a Django datetime object
        end_date = convert_timestamp_to_datetime(endDate)
        created_at = timezone.datetime.fromtimestamp(timestamp, tz=timezone.utc)

        # Fetch the associated event and creator
        try:
            associated_event = Event.objects.get(id=event_id)
            creator_profile = UserProfile.objects.get(wallet_address=associated_event.creator.wallet_address)
        except (Event.DoesNotExist, UserProfile.DoesNotExist):
            # Handle the case where the associated event or user does not exist in the database
            # This might be an error or you might want to create a new event or user
            continue

        # Save the milestone to the database
        milestone_instance, _ = Milestone.objects.get_or_create(
            event=associated_event,
            name=milestone_name,
            milestone_index=milestone_index,
            defaults={
                'creator': creator_profile,
                'description': description,
                'spended_amount': 0,  # Assuming the spended amount starts at 0
                'target_amount': target_amount,
                'end_date': end_date,
                'created_at': created_at,
                'rating_sum': 0,
                'rating_count': 0,
                'committee_id': 0,  # Assuming no committee is assigned initially
                'completed': False,
                'is_fund_released': False,
                'status': status
            }
        )

        contract_obj.save()


def handle_donated_to_event_event():
    contract_obj = Contract.objects.get(contract_name="Fundraising")
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    donated_to_event_events = contract.events.DonatedToEvent().get_logs(
        fromBlock=contract_obj.last_processed_event_block, toBlock="latest")

    for event in donated_to_event_events:
        try:
            donor_address = event['args']['donor']
            amount = Decimal(event['args']['amount'])
            event_id = event['args']['eventId']
            message = event['args']['message']
            block_number = event['blockNumber']
            timestamp = web3.eth.get_block(block_number)["timestamp"]
            event_instance = Event.objects.get(id=event_id)
            donor_profile, created = UserProfile.objects.get_or_create(wallet_address=donor_address)
            Donation.objects.create(
                donor=donor_profile,
                amount=Decimal(amount),
                event=event_instance,
                timestamp=datetime.datetime.fromtimestamp(timestamp),
                message=message
            )
            # Updating the collected_amount of the related Event
            event_instance.collected_amount += Decimal(amount)
            event_instance.save()

        except Exception as e:
            print(e)

def handle_fund_released_to_creator_event():
    contract_obj = Contract.objects.get(contract_name="Fundraising")
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    fund_released_to_creator_events = contract.events.FundReleasedToCreator().get_logs(
        fromBlock=contract_obj.last_processed_event_block, toBlock="latest")

    for event in fund_released_to_creator_events:
        event_id = event['args']['eventId']
        amount = Decimal(event['args']['creatorShare'])
        creator_address = event['args']['creator']

        event_instance = Event.objects.get(id=event_id)
        creator_profile = UserProfile.objects.get(wallet_address=creator_address)

        FundRelease.objects.create(
            event=event_instance,
            amount=amount,
            release_type='Creator',
            recipient=creator_profile
        )


def handle_fund_released_to_validators_event():
    contract_obj = Contract.objects.get(contract_name="Fundraising")
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    fund_released_to_validators = contract.events.FundReleasedToValidators().get_logs(
        fromBlock=contract_obj.last_processed_event_block, toBlock="latest")

    for event in fund_released_to_validators:
        event_id = event['args']['eventId']
        amount = Decimal(event['args']['validatorShare'])
        validator_address = event['args']['validator']

        validator_profile = UserProfile.objects.get(wallet_address=validator_address)
        event_instance = Event.objects.get(id=event_id)
        FundRelease.objects.create(
            event=event_instance,
            amount=amount,
            release_type='Validator',
            recipient=validator_profile
        )


def handle_fund_released_to_platform_event():
    contract_obj = Contract.objects.get(contract_name="Fundraising")
    address = contract_obj.address
    abi = contract_obj.abi
    provider_url = contract_obj.network.rpc_endpoint

    web3 = Web3(Web3.HTTPProvider(provider_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    contract = web3.eth.contract(address=address, abi=abi)

    fund_released_to_platform_events = contract.events.FundReleasedToPlatform().get_logs(
        fromBlock=contract_obj.last_processed_event_block, toBlock="latest")

    for event in fund_released_to_platform_events:
        event_id = event['args']['eventId']
        amount = Decimal(event['args']['platformShare'])
        platform_address = event['args']['platform']

        platform_profile = UserProfile.objects.get(wallet_address=platform_address)
        event_instance = Event.objects.get(id=event_id)
        FundRelease.objects.create(
            event=event_instance,
            amount=amount,
            release_type='Platform',
            recipient=platform_profile
        )
