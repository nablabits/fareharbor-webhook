BIKES_IN_USE_QUERY = """
    -- Redash query: 105
    SELECT distinct bk.uuid
    FROM booking b
    LEFT JOIN availability av ON b.availability_id = av.id
    LEFT JOIN customer c ON c.booking_id = b.id
    LEFT JOIN customer_type_rate ctr ON ctr.id = c.customer_type_rate_id
    LEFT JOIN customer_type ct ON ct.id = ctr.customer_type_id

    LEFT JOIN bike_usages bu ON bu.availability_id = av.id
    LEFT JOIN bike bk ON bk.id = bu.bike_id
    WHERE
        -- The usual filters for bookings: either won't happen or happening at some other
        -- point in th the future.
        b.rebooked_to IS NULL AND b.status != 'cancelled' 

        -- Filter now depending the type of service. For tours we can rely on availability end
        -- date. But for rentals is sigthly more tricky as availabilities last .5h and
        -- durations are represented by customer types

        AND (
                (
                    -- Happy path: tours (excluding walkings)
                    av.item_id IN (159053, 159055, 159056, 159057, 159058, 159060)
                    AND '{target_timestamp}' BETWEEN av.start_at AND av.end_at
                )

                OR
                (
                    -- Unhappy path: rentals
                    av.item_id IN {rentals_ids}  -- rentals
                    AND (
                        (ct.id = 314997 AND '{target_timestamp}' BETWEEN av.start_at AND av.start_at + interval '2 hours')
                        OR (ct.id = 314998 AND '{target_timestamp}' BETWEEN av.start_at AND av.start_at + interval '4 hours')
                        OR (ct.id = 314999 AND '{target_timestamp}' BETWEEN av.start_at AND av.start_at + interval '8 hours')
                        OR (ct.id = 315000 AND '{target_timestamp}' BETWEEN av.start_at AND av.start_at + interval '24 hours')
                        OR (ct.id = 315001 AND '{target_timestamp}' BETWEEN av.start_at AND av.start_at + interval '2 days')
                        OR (ct.id = 315002 AND '{target_timestamp}' BETWEEN av.start_at AND av.start_at + interval '7 days')
                        OR (ct.id = 315003 AND '{target_timestamp}' BETWEEN av.start_at AND av.start_at + interval '24 hours')  -- Extra day
                        OR (ct.id = 601300 AND '{target_timestamp}' BETWEEN av.start_at AND av.start_at + interval '10 days')
                    )
                )
            )
"""
