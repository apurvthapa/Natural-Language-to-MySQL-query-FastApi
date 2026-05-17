schema_dict ={'shipments': '''
Table: shipments

Description:
Contains shipment movement and delivery information.

Columns:

- shipment_id (INT, PRIMARY KEY)
  Unique shipment identifier

- ship_id (INT, FOREIGN KEY -> ships.ship_id)
  Unique ship identifier

- source_port_id (INT, FOREIGN KEY -> ports.port_id)
  Source port of shipment

- destination_port_id (INT, FOREIGN KEY -> ports.port_id)
  Destination port of shipment

- departure_time (DATETIME)
  Timestamp when shipment departed

- estimated_arrival (DATETIME)
  Expected shipment arrival timestamp

- actual_arrival (DATETIME, NULLABLE)
  Actual shipment arrival timestamp.
  NULL means shipment has not arrived yet.

- cargo_type (VARCHAR)
  Type of cargo carried by shipment

  Possible values:
  - Electronics
  - Coal
  - Crude Oil
  - Steel
  - Textiles
  - Automobiles
  - Machinery
  - Food Products
  - Chemicals
  - Consumer Goods

- shipment_status (VARCHAR)
  Current shipment status

  Possible values:
  - Critical Delay
  - Delayed
  - On Time
  - In Transit

- delay_hours (INT, NULLABLE)
  Delay duration in hours.
  Calculated using estimated_arrival and actual_arrival.
  NULL means shipment has not arrived yet.
'''
,
"ports": '''
Table: ports

Description:
Contains ports information

Columns:

- port_id (INT, PRIMARY KEY)
  Unique shipment identifier
  INT value between from 1 to 15

- port_name(VARCHAR)
  Contains port names

  Possible values:
  - Shanghai
  - Singapore
  - Rotterdam
  - Hamburg
  - Dubai
  - Mumbai
  - Los Angeles
  - Long Beach
  - Busan
  - Hong Kong
  - Antwerp
  - New York
  - Tokyo
  - Sydney
  - Chennai

- country(VARCHAR)
  contains the contries where the ports are

  Possible values:
  - China
  - Singapore
  - Netherlands
  - Germany
  - UAE
  - India
  - USA
  - South Korea
  - Belgium
  - Japan
  - Australia

- region(VARCHAR)
  Region where the country are

  Possible values:
  - Asia
  - Europe
  - Middle East
  - North America
  - Oceania
'''
,
"ships" :'''
Table: ships

Description:
Contains ships details

Columns:

- ship_id (INT, PRIMARY KEY)
  Unique ships identifier
  INT value between from 1 to 1000

- ship_name (VARCHAR)
  Name of respective ships

- vessel_type (VARCHAR)
  Vessel types

  Possible values:
  - Refrigerated Cargo
  - Oil Tanker
  - LNG Carrier
  - Bulk Carrier
  - Cargo
  - Vehicle Carrier
  - Container

- operator_company (VARCHAR)
  Ship owned by operator

  Possible values:
  - ONE
  - ZIM
  - CMA CGM
  - MSC
  - Hapag-Lloyd
  - COSCO Shipping
  - HMM
  - Maersk
  - Evergreen Marine
  - Yang Ming

- capacity_teu(INT)
  Ship capacity in Kilo-Tonne

- origin_country
  Country name from where the ship originated


'''
             }