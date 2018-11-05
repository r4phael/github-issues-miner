from pymongo import MongoClient
from bson.objectid import ObjectId

# Step 1: Connect to MongoDB - Note: Change connection string as needed
client = MongoClient(port=27017)
db = client.reviews
# Step 2: Create sample data
query_results = db.issues.find_one({'project': 'Elasticsearch-Hadoop'})

project_id = str(query_results.get('_id'))
print(project_id)

query_results = db.issues.find_one({'_id': ObjectId(project_id), 'issues.number': {'$eq': 1173}})
print('Query Find_one: ' + str(query_results))

# query_results = db.issues.delete_one({"issues.number": {"$eq": 1192}})
#query_results = db.issues.update({'_id': ObjectId(project_id)}, {'$pull': {'issues': {'number': 1178}}})
#print(query_results)

#TODO: ImportJson from github and make 3 opetarions:  1.add the databse of project, 2.find in database, 3.delete one issue on push, 4.add one issue with pull.