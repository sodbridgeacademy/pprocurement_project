from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from accounts.models import User 
from .serializers import OrderFileUploadSerializer
import re

class OrderFileUploadAPIView(APIView):
    def post(self, request):
        serializer = OrderFileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            try:
                # Read the contents of the uploaded file
                file_content = file.read().decode('utf-8')

                # Split the file content into lines
                lines = file_content.split('\n')

                # Iterate over each line and process the order information
                for line in lines:
                    # Extract procurement officer name from the line
                    match = re.match(r'^=+ (.+) =+$', line)
                    if match:
                        procurement_officer_name = match.group(1).strip()
                        # Query the database to find the user by name
                        procurement_officer = User.objects.filter(username=procurement_officer_name).first()
                        if procurement_officer:
                            # Process orders for this procurement officer
                            continue  # You can handle order processing here
                        else:
                            return Response({'error': f'Procurement officer "{procurement_officer_name}" not found'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'success': 'File uploaded successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
