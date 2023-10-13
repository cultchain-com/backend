from rest_framework.response import Response
from .models import Contract
from .serializers import ContractABISerializer
from web3 import Web3

class ImportContractABIView(generics.CreateAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractABISerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)