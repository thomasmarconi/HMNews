#!/bin/bash
sudo systemctl stop hmnews
sudo systemctl daemon-reload
sudo systemctl start hmnews
sudo systemctl enable hmnews
sudo systemctl status hmnews
sudo systemctl start hmnews
