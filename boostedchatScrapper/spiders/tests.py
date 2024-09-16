def insert_and_enrich(keywords_to_check, round_number):
    instagram_users = InstagramUser.objects.filter(round=round_number)
    hour = 4
    for i, instagram_user in enumerate(instagram_users):
        if instagram_user.username and not instagram_user.info.get('is_private'):
            # import pdb;pdb.set_trace()
            try:
                with engine.connect() as connection:
                    try:
                        existing_username_query = select([instagram_account_table]).where(
                            instagram_account_table.c.igname == instagram_user.username
                        )
                    except Exception as err:
                        try:
                            existing_username_query = select(instagram_account_table).where(
                                instagram_account_table.c.igname == instagram_user.username
                            )
                        except Exception as err:
                            print(err)
                    existing_username = connection.execute(existing_username_query).fetchone()
                    print(existing_username)
                    if existing_username:
                    #     pass
                    # else:
                        insert_statement = instagram_account_table.insert().values(
                            id=str(uuid.uuid4()),
                            created_at=timezone.now(),
                            updated_at=timezone.now(),
                            igname=instagram_user.username,
                            full_name=instagram_user.info.get('full_name', ''),
                            assigned_to="Robot",
                            dormant_profile_created=True,
                            qualified=False,
                            index=1,
                            linked_to="not"
                        ).returning(instagram_account_table.c.id)

                        account_id = connection.execute(insert_statement).fetchone()[0]

                        insert_statement = inst.instagram_outsourced_table.insert().values(
                            id=str(uuid.uuid4()),
                            created_at=timezone.now(),
                            updated_at=timezone.now(),
                            source="ig",
                            results=instagram_user.info,
                            account_id=account_id
                        ).returning(inst.instagram_outsourced_table.c.results)

                        record = connection.execute(insert_statement).fetchone()
                        qualified,keyword_counts = inst.qualify(record[0], keywords_to_check, datetime.now() + timedelta(hours=hour))
                        if qualified:
                            print("--------------------------------------------------------wewe--------------------------------------")
                            filtered_dict = {key: value for key, value in keyword_counts.items() if value >= 1}
                            instagram_user.qualified_keywords = str(filtered_dict)
                            instagram_user.qualified = True
                            instagram_user.save()
                            inst.assign_salesreps(instagram_user.username, i)

            except Exception as error:
                print(error)