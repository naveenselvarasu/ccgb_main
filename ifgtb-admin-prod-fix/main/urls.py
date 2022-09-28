from django.urls import re_path
from main import views

urlpatterns = [
    # logins and otp 
    re_path(r'^portal/login/for/token/$', views.portal_login_for_token),
    re_path(r'^username/validation/$', views.username_validation),
    re_path(r'^otp/validation/$', views.otp_validation),
    re_path(r'^reset/password/$', views.reset_password),
    re_path(r'^serve/industry/list/$', views.serve_industry),
    re_path(r'^website/login/for/token/$', views.website_login_for_token),
    # forget password
    re_path(r'^app/login/for/token/$', views.login_for_token),

    # mobile app
    re_path(r'^serve/otp/for/registration/$', views.serve_otp_for_registration),
    re_path(r'^otp/validation/for/farmer/registration/$', views.otp_validation_for_farmer_registration),
    re_path(r'^serve/user/types/$', views.serve_user_types),
    re_path(r'^serve/farmer/lands/$', views.serve_farmer_lands),
    re_path(r'^serve/farmer/crops/$', views.serve_farmer_crops),
    re_path(r'^username/validation/$', views.username_validation),
    re_path(r'^serve/child/pages/$', views.serve_child_pages),
    re_path(r'^serve/helpline/multi/language/json/$', views.serve_helpline_json_for_app),
    re_path(r'^register/expensive/$', views.register_expansive),
    re_path(r'^serve/expensive/for/crop/$', views.serve_expensive_for_crop),
    re_path(r'^serve/farmer/dashboard/data/$', views.serve_farmer_dashboard_data),
    

    # website
    # common
    re_path(r'^serve/castes/$', views.serve_castes),
    re_path(r'^serve/gender/$', views.serve_gender),
    re_path(r'^serve/language/list/$', views.serve_language),
    re_path(r'^serve/state/district/block/rev_village/$', views.serve_state_district_block_rev_village),
    re_path(r'^register/farmer/$', views.register_farmer),
    re_path(r'^register/land/$', views.register_land),
    re_path(r'^serve/lands/$', views.serve_lands),
    re_path(r'^register/crop/$', views.register_crop),
    re_path(r'^serve/crop/cvs/$', views.serve_crop_cvs),
    re_path(r'^serve/geo/tag/fence/for/selected/filter/$', views.serve_geo_tag_fence_for_selected_filter),

    # Dynamic question
    re_path(r'^webservice/serve/questions/$', views.serve_questions),
    re_path(r'^save/dynamic/questions/answers/$', views.save_dynamic_questions_answers),
    re_path(r'^serve/dynamic/questions/answers/$', views.serve_farmer_dynamic_questions_answers),

    re_path(r'^serve/languages/$', views.serve_languages),
    re_path(r'^serve/language/translation/$', views.serve_language_translation),
    re_path(r'^serve/crop/expence/details/$', views.serve_crop_expence_details),

    # harvest
    re_path(r'^register/harvest/$', views.register_harvest),
    re_path(r'^serve/harvest/log/$', views.serve_harvest_log),
    re_path(r'^serve/harvest/units/$', views.serve_harvest_units),
    re_path(r'^register/or/update/language/preference/$', views.register_or_update_language_preference),
    re_path(r'^serve/water/sources/$', views.serve_water_sources),
    re_path(r'^serve/water/types/$', views.serve_water_types),
    re_path(r'^serve/ownership/$', views.serve_ownership),
    re_path(r'^save/farmer/area/and/ownership/$', views.save_farmer_area_and_ownership),
    re_path(r'^register/minimal/land/crop/register/$', views.register_minimal_land_crop_register),
    re_path(r'^register/water/resource/$', views.register_water_resource),
    re_path(r'^register/single/water/resource/$', views.register_single_water_resource),


    #pages micro service
    re_path(r'^serve/featured/video/link/$', views.serve_featured_video_link),
    re_path(r'^serve/faq/pages/from/ms/$', views.serve_faq_child_pages),
    re_path(r'^serve/raq/pages/from/ms/$', views.serve_raq_child_pages),
    re_path(r'^serve/advisory/pages/from/ms/$', views.serve_advisory_child_page),
    re_path(r'^serve/url/for/pdf/and/videos/from/ms/$', views.serve_url_for_pdf_and_video),
    re_path(r'^serve/industry/details/for/stakeholder/directory/$', views.serve_industry_details_for_stakeholder_directory),
    re_path(r'^serve/qpm/nursery/details/for/stakeholder/directory/$', views.serve_qpm_nursery_details_for_stakeholder_directory),
    re_path(r'^serve/ifgtb/scientist/details/for/stakeholder/directory/$', views.serve_ifgtb_scientist_details_for_stakeholder_directory),
    re_path(r'^serve/farmer/details/for/stakeholder/directory/from/farmer/ms/$',views.serve_farmer_details_for_stakeholder_directory_from_farmer_ms),


    #farmer profile
    re_path(r'^serve/farmer/basic/info/$', views.serve_farmer_basic_info),
    re_path(r'^serve/farmers/basic/info/data/$', views.serve_farmers_basic_info_data),
    re_path(r'^serve/land/detail/by/id/$', views.serve_land_detail_by_id),
    re_path(r'^serve/crop/detail/by/id/$', views.serve_crop_detail_by_id),
    re_path(r'^serve/water/resource/detail/by/id/$', views.serve_water_resource_detail_by_id),
    re_path(r'^serve/farmer/detail/by/id/$', views.serve_farmer_detail_by_id),
    re_path(r'^update/farmer/$', views.update_farmer),
    re_path(r'^update/farmer/via/portal/$', views.update_farmer_via_portal),
    re_path(r'^update/geo/location/$', views.update_geo_location),
    re_path(r'^serve/geo/fence/data/$', views.serve_geo_fence_data),
    re_path(r'^upload/geo/fence/gps/data/$', views.upload_geo_fence_gps_data),
    re_path(r'^update/or/create/farmer/profile/$', views.update_or_create_farmer_profile),
    re_path(r'^serve/user/type/tile/list/$', views.serve_user_type_tile_list),
    re_path(r'^serve/youtube/video/by/play/list/id/$', views.serve_youtube_video_by_play_list_id),
    re_path(r'^serve/google/album/$', views.serve_google_album),
    re_path(r'^get/photos/inside/album/$', views.get_photos_inside_album),
    re_path(r'^post/data/to/farmer/server/$', views.post_data_to_farmer_server),
    re_path(r'^serve/crop/clone/$', views.serve_crop_clone),
    re_path(r'^create/crop/clone/$', views.create_crop_clone),
    
    re_path(r'^delete/crop/clone/$', views.delete_crop_clone),
    re_path(r'^update/crop/clone/$', views.update_crop_clone),

    # farmer profile data
    re_path(r'^serve/farmer/basic/details/$', views.serve_farmer_basic_details),
    re_path(r'^update/farmer/basic/details/$', views.update_farmer_basic_details),

    # qpm
    re_path(r'^serve/qpm/basic/details/$', views.serve_qpm_basic_details),
    re_path(r'^update/qpm/basic/details/$', views.update_qpm_basic_details),
    re_path(r'^update/forest/basic/details/$', views.update_forest_basic_details),

    
    # industry
    re_path(r'^serve/industry/basic/details/$', views.serve_industry_basic_details),
    re_path(r'^update/industry/basic/details/$', views.update_industry_basic_details),

    # industry
    re_path(r'^serve/scientist/basic/details/$', views.serve_scientist_basic_details),
    re_path(r'^update/scientist/basic/details/$', views.update_scientist_basic_details),

    #update profile picture
    re_path(r'^update/profile/photo/$', views.update_profile_photo),

    # Portal
    re_path(r'^serve/industry/list/$', views.serve_industry),
    re_path(r'^save/industry/$', views.save_industry),
    re_path(r'^serve/industry/branches/$', views.serve_industry_branches),
    re_path(r'^save/industry/branch/$', views.save_industry_branch),
    re_path(r'^get/industry/office/list/$', views.serve_industry_office_list),
    re_path(r'^save/industry/users/$', views.save_industry_users),
    re_path(r'^get/industry/user/list/$', views.get_industry_user_list),

    re_path(r'^save/institute/$', views.save_institute),
    re_path(r'^serve/institute/list/$', views.serve_institute),
    re_path(r'^save/institute/branch/$', views.save_institute_branch),
    re_path(r'^serve/institute/branches/$', views.serve_institute_branches),
    re_path(r'^save/institute/users/$', views.save_institute_users),
    re_path(r'^serve/institute/office/list/$', views.serve_institute_office_list),
    re_path(r'^serve/institute/users/list/$', views.get_institute_user_list),


    re_path(r'^get/nursery/list/$', views.serve_nursery),
    re_path(r'^save/nursery/$', views.save_nursery),
    re_path(r'^save/nursery/branch/$', views.save_nursery_branch),
    re_path(r'^serve/nursery/branches/$', views.serve_nursery_branches),
    re_path(r'^serve/nursery/users/list/$', views.get_nursery_user_list),
    re_path(r'^serve/nursery/office/list/$', views.serve_nursery_office_list),
    re_path(r'^save/nursery/users/$', views.save_nursery_users),


    re_path(r'^serve/forest/list/$', views.serve_forest),
    re_path(r'^get/forest/office/list/$', views.serve_forest_office_list),
    re_path(r'^serve/forest/branches/$', views.serve_forest_branches),
    re_path(r'^get/forest/user/list/$', views.get_forest_user_list),
    re_path(r'^save/forest/$', views.save_forest),
    re_path(r'^save/forest/branch/$', views.save_forest_branch),
    re_path(r'^save/forest/users/$', views.save_forest_users),

    re_path(r'^serve/usertype/role/menu/$', views.serve_usertype_role_menu),
    re_path(r'^serve/farmer/bulk/uploaded/detalils/$', views.serve_farmer_bulk_uploaded_detalils),
    re_path(r'^farmer/bulk/register/$', views.farmer_bulk_register),
    re_path(r'^serve/all/scientist/$', views.serve_all_scientist),
    re_path(r'^serve/assigned/scientist/list/$', views.serve_assigned_scientist_list),
    re_path(r'^serve/experties/list/$', views.serve_experties_list),
    re_path(r'^remove/scientists/$', views.remove_scientists),
    
    
    # stack holders
    re_path(r'^serve/farmer/details/for/selected/id/$', views.serve_farmer_details_for_selected_id),
    re_path(r'^serve/qpm/details/for/selected/id/$', views.serve_qpm_details_for_selected_id),
    re_path(r'^serve/industry/basic/details/for/given/id/$', views.serve_industry_basic_details_for_given_id),
    re_path(r'^serve/ifgtb/basic/details/for/given/id/$', views.serve_ifgtb_basic_details_for_given_id),

    
    re_path(r'^serve/forest/stack/holders/$', views.serve_forest_stack_holders),
    re_path(r'^get/forest/details/for/given/id/$', views.get_forest_details_for_given_id),


    # forest
    re_path(r'^serve/forest/basic/details/$', views.serve_forest_basic_details),
    re_path(r'^create/crop/clone/forest/$', views.create_crop_clone_forest),
    re_path(r'^serve/crop/clone/forest/$', views.serve_crop_clone_forest),
    re_path(r'^delete/crop/clone/forest/$', views.delete_crop_clone_forest),
    re_path(r'^update/crop/clone/forest/$', views.update_crop_clone_forest),
    re_path(r'^serve/branches/industry/$', views.serve_branches_for_industry),
    re_path(r'^serve/farmers/location/with/crop/$', views.serve_farmers_location_with_crop),
    re_path(r'^farmer/geo/fence/data/register/$', views.farmer_geo_fence_data_register),
    
    # check for authentication
    re_path(r'^check/authentication/$', views.check_for_authentication),

    # check for farmer exists
    re_path(r'^check/for/farmer/$', views.check_for_farmer),

    # serve field officer registered farmer list 
    re_path(r'^get/farmer/list/for/field/officer/$', views.farmer_list_for_field_officer),

    #surveyor
    re_path(r'^get/user/type/surveyor/$', views.get_user_type_for_surveyor),
    re_path(r'^save/surveyor/official/map/$', views.surveyor_official_map_save),
    re_path(r'^get/surveyor/list/$', views.get_surveyor_list),
    re_path(r'^to/update/surveyor/data/$', views.to_update_surveyor),
    re_path(r'^to/delete/surveyor/data/$', views.to_delete_surveyor),
    re_path(r'^serve/surveyor/basic/details/$', views.serve_surveyor_basic_details),
    re_path(r'^update/surveyor/basic/details/$', views.update_surveyor_basic_details),
    re_path(r'^get/notification/for/admin/$', views.get_notification_for_admin),
    re_path(r'^get/notification/for/scientist/$', views.get_notification_for_scientist),
    re_path(r'^serve/category/list/$', views.serve_category),
    re_path(r'^serve/journals/$', views.serve_journals),
    re_path(r'^store/journals/$', views.store_journal),
    re_path(r'^disable/notifications/$', views.disable_notifications),
    re_path(r'^get/notification/for/farmer/$', views.get_notification_for_farmer),
    re_path(r'^save/fcm/device/token/$', views.save_fcm_device_token),
    re_path(r'^serve/district/wise/data/$', views.serve_district_wise_data),
    re_path(r'^send/notification/to/users/$', views.send_notification_to_users),
    
    re_path(r'^get/iframe/$', views.get_iframe),
    re_path(r'^save/prcurement/price/industry/$', views.save_procurement_price_industry),
    re_path(r'^serve/crop/$', views.serve_crop),

    re_path(r'^serve/products/$', views.serve_products),
    re_path(r'^serve/user/manual/$', views.serve_user_manual),
    re_path(r'^serve/publication/$', views.serve_publication),
    re_path(r'^disable/notification/from/ask/expert/$', views.disable_notifications_from_ask_expert),
    re_path(r'^disable/notification/from/recommendation/$', views.disable_notifications_from_recommendation),
    re_path(r'^clear/notifications/$', views.clear_notifications)
    
]   
