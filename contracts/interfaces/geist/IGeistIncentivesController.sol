// SPDX-License-Identifier: agpl-3.0
pragma solidity 0.6.12;

interface IGeistIncentivesController {
    function addPool(address _token, uint256 _allocPoint) external;

    function batchUpdateAllocPoint(
        address[] memory _tokens,
        uint256[] memory _allocPoints
    ) external;

    function claim(address _user, address[] memory _tokens) external;

    function claimReceiver(address) external view returns (address);

    function claimableReward(address _user, address[] memory _tokens)
        external
        view
        returns (uint256[] memory);

    function emissionSchedule(uint256)
        external
        view
        returns (uint128 startTimeOffset, uint128 rewardsPerSecond);

    function handleAction(
        address _user,
        uint256 _balance,
        uint256 _totalSupply
    ) external;

    function maxMintableTokens() external view returns (uint256);

    function mintedTokens() external view returns (uint256);

    function owner() external view returns (address);

    function poolConfigurator() external view returns (address);

    function poolInfo(address)
        external
        view
        returns (
            uint256 totalSupply,
            uint256 allocPoint,
            uint256 lastRewardTime,
            uint256 accRewardPerShare,
            address onwardIncentives
        );

    function poolLength() external view returns (uint256);

    function registeredTokens(uint256) external view returns (address);

    function renounceOwnership() external;

    function rewardMinter() external view returns (address);

    function rewardsPerSecond() external view returns (uint256);

    function setClaimReceiver(address _user, address _receiver) external;

    function setOnwardIncentives(address _token, address _incentives) external;

    function start() external;

    function startTime() external view returns (uint256);

    function totalAllocPoint() external view returns (uint256);

    function transferOwnership(address newOwner) external;

    function userInfo(address, address)
        external
        view
        returns (uint256 amount, uint256 rewardDebt);
}
