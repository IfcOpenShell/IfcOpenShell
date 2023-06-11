import ifcopenshell
import ifcopenshell.util.element
import boto3

s3 = boto3.client('s3')

def extract_wall_psets_handler(event, context):
    print("Hello from lambda")
    print("Event: {}".format(event))
    print("Context: {}".format(context))

    filename = event['body']['filename']
    
    s3.download_file('my_ifc_files_bucket', filename, f'/tmp/{filename}')
    ifc_file = ifcopenshell.open(f'/tmp/{filename}')
    walls = ifc_file.by_type('IfcWall')
    
    psets = []
    for wall in walls:
        wall_data = ifcopenshell.util.element.get_psets(wall)
        wall_data['id'] = wall.GlobalId
        psets.append(wall_data)

    return {
        'statusCode': 200,
        'body': psets
    }