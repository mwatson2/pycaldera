# swagger_client.DefaultApi

All URIs are relative to *https://connectedspa.watkinsmfg.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**connextion_auth_login_post**](DefaultApi.md#connextion_auth_login_post) | **POST** /connextion/auth/login | 
[**connextion_spa_my_spas_post**](DefaultApi.md#connextion_spa_my_spas_post) | **POST** /connextion/spa/my-spas | 

# **connextion_auth_login_post**
> connextion_auth_login_post(body=body)



### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.AuthLoginBody() # AuthLoginBody |  (optional)

try:
    api_instance.connextion_auth_login_post(body=body)
except ApiException as e:
    print("Exception when calling DefaultApi->connextion_auth_login_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AuthLoginBody**](AuthLoginBody.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **connextion_spa_my_spas_post**
> connextion_spa_my_spas_post(body=body)



### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint


# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
body = {
  "value" : "{}"
} # object |  (optional)

try:
    api_instance.connextion_spa_my_spas_post(body=body)
except ApiException as e:
    print("Exception when calling DefaultApi->connextion_spa_my_spas_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[TokenCredentials](../README.md#TokenCredentials)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

