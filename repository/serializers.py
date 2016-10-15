from rest_framework import serializers
from repository.models import Repository, DigitalEvidence, ElectronicEvidence
from .models import User

class RepositorySerializers(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='user.email')
    digital = serializers.HyperlinkedRelatedField(many=True, view_name='digital-detail', read_only=True)
    electronic = serializers.HyperlinkedRelatedField(many=True, view_name='electronic-detail', read_only=True)
    class Meta:
        model = Repository
        fields = ('url', 'id_repository', 'repository_name', 'info','owner', 'created', 'date', 'digital', 'electronic')

class DigitalEvidenceSerializers(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='repository.user.email')
    class Meta:
        model = DigitalEvidence
        fields = ('id', 'repository','filename', 'file', 'info_file','owner')

class ElectronicEvidenceSerializers(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='repository.user.email')
    class Meta:
        model = ElectronicEvidence
        fields = ('id', 'repository', 'filename', 'file','info_file', 'owner')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    repository = serializers.HyperlinkedRelatedField(many=True, view_name='repository-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url','pk','email','repository')

