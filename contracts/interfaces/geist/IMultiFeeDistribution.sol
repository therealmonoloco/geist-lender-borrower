// SPDX-License-Identifier: agpl-3.0
pragma solidity 0.6.12;

interface IMultiFeeDistribution {
    // Withdraw full unlocked balance and claim pending rewards
    function exit() external;
}