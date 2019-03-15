	consumerCfg := &kafka.ConfigMap{
		"group.id":                        cfg.GroupId,
		"client.id":                       "umb-cli",
		"bootstrap.servers":               strings.Join(cfg.Brokers, ","),
		"security.protocol":               "SSL",
		"ssl.ca.location":                 cfg.ClusterCert,
		"ssl.certificate.location":        cfg.ClientCert,
		"ssl.key.location":                cfg.ClientKey,
		"session.timeout.ms":              6000,
		"go.events.channel.enable":        true,
		"go.application.rebalance.enable": true,
		"default.topic.config":            kafka.ConfigMap{"auto.offset.reset": "latest"},
	}
	if cfg.Debug {
		consumerCfg.SetKey("debug", "generic,security,cgrp,protocol")
	}
	c, err := kafka.NewConsumer(consumerCfg)
	if err != nil {
		return errors.Wrap(err, "Creating new consumer")
	}

	err = c.Subscribe(cfg.Topic, nil)
	if err != nil {
		return errors.Wrap(err, "Setting up subscription")
	}
	fmt.Printf("Subscribed to topic %s in group %s\n", cfg.Topic, cfg.GroupId)
	if cfg.Tenants != nil && len(cfg.Tenants) > 0 {
		fmt.Println("Limiting consumption to tenants:")
		for _, tenantId := range cfg.Tenants {
			fmt.Printf("* %s\n", tenantId)
		}
	}

	sigchan := make(chan os.Signal, 1)
	signal.Notify(sigchan, syscall.SIGINT, syscall.SIGTERM)

	run := true
	for run {
		select {
		case <-sigchan:
			run = false

		case ev := <-c.Events():
			switch e := ev.(type) {
			case kafka.AssignedPartitions:
				if cfg.Debug {
					fmt.Fprintf(os.Stderr, "%% %v\n", e)
				}
				c.Assign(e.Partitions)
			case kafka.RevokedPartitions:
				if cfg.Debug {
					fmt.Fprintf(os.Stderr, "%% %v\n", e)
				}
				c.Unassign()
			case *kafka.Message:
				key := string(e.Key)
				if cfg.include(key) {
					fmt.Printf("%% Message on %s (key=%s):\n",
						e.TopicPartition, key)
					if len(e.Headers) > 0 {
						fmt.Print("% Headers:{")
						for i, header := range e.Headers {
							if i > 0 {
								fmt.Print(", ")
							}
							fmt.Printf("%s=%s", header.Key, string(header.Value))
						}
						fmt.Println("}")
					}
					fmt.Println(string(e.Value))
				} else if cfg.Debug {
					fmt.Printf("%% EXCLUDED message on %s (key=%s):\n%s\n",
						e.TopicPartition, key, string(e.Value))
				}
			case kafka.PartitionEOF:
				if cfg.Debug {
					fmt.Printf("%% Reached %v\n", e)
				}
			case kafka.Error:
				fmt.Fprintf(os.Stderr, "%% Error: %v\n", e)
				run = false
			}
		}
	}
	fmt.Println("Closing consumer")
	c.Close()

