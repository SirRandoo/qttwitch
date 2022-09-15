"""
The MIT License (MIT)

Copyright (c) 2021 SirRandoo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
import datetime
import json
import math
from typing import AnyStr, Optional, TYPE_CHECKING, Dict, List, Union

from PySide6 import QtCore, QtNetwork

from QtUtilities import requests, signals

if TYPE_CHECKING:
    PARAMS = Dict[str, Union[str, List[str]]]
    DATA = Union[AnyStr, QtCore.QBuffer]
    HEADERS = Dict[str, str]

__all__ = ['Http']


class Http:
    # TODO: Properly handle metadata ratelimits
    HELIX: str = 'https://api.twitch.tv/helix'

    def __init__(self, client_id: str, token: str = None, factory: requests.Factory = None):
        self.client_id: str = client_id
        self.token: Optional[str] = token
        self.factory: requests.Factory = factory

        if self.factory is None:
            self.factory = requests.Factory()

    # Requests
    def request(self, op: str, endpoint: str = None, *, params: PARAMS = None, headers: HEADERS = None,
                data: DATA = None, request: QtNetwork.QNetworkRequest = None) -> requests.Response:
        api = QtCore.QUrl(f'{self.HELIX.rstrip("/")}/{endpoint}')
        api.setQuery(self.build_query(**params))

        if request is None:
            request = QtNetwork.QNetworkRequest(api)

            for key, value in headers.items():
                request.setRawHeader(QtCore.QByteArray(key.encode()), QtCore.QByteArray(value.encode()))

        if not request.hasRawHeader(QtCore.QByteArray(b'Client-ID')):
            request.setRawHeader(QtCore.QByteArray(b'Client-ID'), QtCore.QByteArray(self.client_id.encode()))

        if not request.hasRawHeader(QtCore.QByteArray(b'Authorization')):
            request.setRawHeader(QtCore.QByteArray(b'Authorization'), QtCore.QByteArray(f'OAuth {self.token}'.encode()))

        response = self.factory.request(op, request=request, data=data)

        if response.code == 401:
            msg = 'Unauthorized'

            if response.is_okay():
                msg = response.json().get('message')

            raise PermissionError(msg)

        if response.code == 429:
            timeout = float(response.headers['Ratelimit-Reset'])
            date = datetime.datetime.fromtimestamp(timeout, tz=datetime.timezone.utc)
            diff = date - datetime.datetime.now(tz=datetime.timezone.utc)

            timer = QtCore.QTimer()

            timer.start(int(math.ceil(diff.total_seconds() * 1000)))
            signals.wait_for_signal(timer.timeout)

            timer.stop()
            timer.deleteLater()

            return self.request(op, request, data=data)

    def get(self, endpoint: str = None, *, params: PARAMS = None, headers: HEADERS = None,
            request: QtNetwork.QNetworkRequest = None) -> requests.Response:
        return self.request('GET', endpoint=endpoint, params=params, headers=headers, request=request)

    def put(self, endpoint: str = None, *, params: PARAMS = None, headers: HEADERS = None, data: DATA = None,
            request: QtNetwork.QNetworkRequest = None) -> requests.Response:
        return self.request('PUT', endpoint=endpoint, params=params, headers=headers, data=data, request=request)

    def post(self, endpoint: str = None, *, params: PARAMS = None, headers: HEADERS = None, data: DATA = None,
             request: QtNetwork.QNetworkRequest = None) -> requests.Response:
        return self.request('POST', endpoint=endpoint, params=params, headers=headers, data=data, request=request)

    def delete(self, endpoint: str = None, *, params: PARAMS = None, headers: HEADERS = None, data: DATA = None,
               request: QtNetwork.QNetworkRequest = None) -> requests.Response:
        return self.request('DELETE', endpoint=endpoint, params=params, headers=headers, data=data, request=request)

    def patch(self, endpoint: str = None, *, params: PARAMS = None, headers: HEADERS = None, data: DATA = None,
              request: QtNetwork.QNetworkRequest = None) -> requests.Response:
        return self.request('PATCH', endpoint=endpoint, params=params, headers=headers, data=data, request=request)

    # Utility methods
    @staticmethod
    def validate_query(**kwargs) -> PARAMS:
        p = kwargs.copy()

        for k, v in kwargs.items():
            if v is None:
                del p[k]

        return p

    @staticmethod
    def build_query(**kwargs) -> QtCore.QUrlQuery:
        params = {k: v for k, v in kwargs.items() if v is not None}

        q = QtCore.QUrlQuery()

        for k, v in params.items():
            if isinstance(v, list) and all(isinstance(i, str) for i in v):
                i: str
                for i in v:
                    q.addQueryItem(k, i)

            else:
                q.addQueryItem(k.encode(), str(v))

        return q

    # Endpoints
    def validate_token(self, token: str = None) -> dict:
        """Validates a token."""
        req = QtNetwork.QNetworkRequest(QtCore.QUrl('https://id.twitch.tv/oauth2/validate'))

        if token is not None:
            req.setRawHeader(QtCore.QByteArray(b'Authorization'), QtCore.QByteArray(f'OAuth {token}'.encode()))

        return self.get(request=req).json()

    def get_extension_analytics(self, *, after: str = None, ended_at: str = None,
                                extension_id: str = None, first: int = None,
                                started_at: str = None, report_type: str = None) -> dict:
        if first is not None:
            if first > 100:
                raise ValueError('Parameter "first" cannot be greater than 100.')

            if first < 0:
                raise ValueError('Parameter "first" cannot be lower than 0.')

        if report_type is not None and report_type.lower() not in ['overview_v1', 'overview_v2']:
            raise ValueError('Parameter "report_type" can only be "overview_v1" or "overview_v2".')

        return self.get(
            'analytics/extensions',
            params=self.validate_query(
                after=after,
                ended_at=ended_at,
                extension_id=extension_id,
                first=first,
                started_at=started_at,
                type=report_type
            )
        ).json()

    def get_game_analytics(self, *, after: str = None, ended_at: str = None,
                           first: int = None, game_id: str = None,
                           started_at: str = None, report_type: str = None) -> dict:
        if first is not None:
            if first > 100:
                raise ValueError('Parameter "first" cannot be greater than 100.')

            if first < 0:
                raise ValueError('Parameter "first" cannot be lower than 0.')

        if report_type is not None and report_type.lower() not in ['overview_v1', 'overview_v2']:
            raise ValueError('Parameter "report_type" can only be "overview_v1" or "overview_v2".')

        return self.get(
            'analytics/games',
            params=self.validate_query(
                after=after,
                ended_at=ended_at,
                first=first,
                game_id=game_id,
                started_at=started_at,
                type=report_type
            )
        ).json()

    def get_bits_leaderboard(self, *, count: int = None, period: str = None,
                             started_at: str = None, user_id: str = None) -> dict:
        if count is not None and count > 100:
            raise ValueError('Parameter "count" cannot be greater than 100.')

        if period is not None and period not in ['all', 'day', 'week', 'month', 'year']:
            raise ValueError('Parameter "period" can only be "all", "day", "week", "month", or "year"')

        return self.request(
            'GET',
            'bits/leaderboard',
            params=self.validate_query(
                count=count,
                period=period,
                started_at=started_at,
                user_id=user_id
            )
        ).json()

    def get_extension_transactions(self, extension_id: str, *,
                                   transaction_id: Union[str, List[str]] = None,
                                   after: str = None, first: int = None) -> dict:
        if isinstance(transaction_id, list) and len(transaction_id) > 100:
            raise ValueError('Parameter "transaction_id" cannot exceed 100 items.')

        if first is not None:
            if first > 100:
                raise ValueError('Parameter "first" cannot be greater than 100.')

            if first < 0:
                raise ValueError('Parameter "first" cannot be less than 0.')

        u = QtCore.QUrl(f'{self.HELIX}/extensions/transactions')
        u.setQuery(self.build_query(extension_id=extension_id, id=transaction_id, after=after, first=first))

        return self.get(request=QtNetwork.QNetworkRequest(u)).json()

    # noinspection SpellCheckingInspection
    def create_clip(self, broadcaster_id: str, *, has_delay: bool = None) -> dict:
        """Creates a clip programmatically.  This returns both an ID and an edit
        URL for the new clip.

        Clip creation takes time.  We recommend that you query `Get Clips`, with
        the clip ID that is returned here.  If the Get Clips returns a valid
        clip, your clip creation was successful.  If, after 15 seconds, you
        still have not gotten back a valid clip from Get Clips, assume that the
        clip was not created and retry Create Clip.

        This endpoint has a global rate limit, across all callers.  The limit
        may change over time, but the response includes informative headers:

        +----------------------------------------+---------+
        |                    Name                |  Value  |
        +========================================+=========+
        | Ratelimit-Helixclipscreation-Limit     | integer |
        +----------------------------------------+---------+
        | Ratelimit-Helixclipscreation-Remaining | integer |
        +----------------------------------------+---------+

        * Required scope: `clips:edit`"""
        r = self.post('clips', params=self.build_query(broadcaster_id=broadcaster_id, has_delay=has_delay))

        if r.headers.get('Ratelimit-Helixclipscreation-Remaining', 0) <= 0:
            reset = r.headers.get('Ratelimit-Helixclipscreation-Reset')

            if reset is not None:
                parsed = datetime.datetime.fromtimestamp(reset, tz=datetime.timezone.utc)
                diff = datetime.datetime.now(tz=datetime.timezone.utc) - parsed

                timer = QtCore.QTimer()
                timer.start(math.ceil(diff.total_seconds()))
                signals.wait_for_signal(timer.timeout)
                return self.create_clip(broadcaster_id=broadcaster_id, has_delay=has_delay)

        return r.json()

    def get_clips(self, broadcaster_id: str = None, game_id: str = None,
                  clip_id: Union[str, List[str]] = None, *, after: str = None, before: str = None,
                  ended_at: str = None, first: int = None, started_at: str = None) -> dict:
        if broadcaster_id is None and game_id is None and clip_id is None:
            raise ValueError('Missing a required parameter (broadcaster_id, game_id, or clip_id is required)')

        if isinstance(clip_id, list):
            if len(clip_id) > 100:
                raise ValueError('Parameter "clip_id" cannot have more than 100 entries!')

            if len(clip_id) <= 0:
                raise ValueError('Parameter "clip_id" must have at least one entry.')

        if first is not None and first > 100:
            raise ValueError('Parameter "first" cannot be greater than 100.')

        u = QtCore.QUrl(f'{self.HELIX}/clips')
        u.setQuery(self.build_query(
            broadcaster_id=broadcaster_id,
            game_id=game_id,
            id=clip_id,
            after=after,
            before=before,
            ended_at=ended_at,
            first=first,
            started_at=started_at
        ))

        return self.get(request=QtNetwork.QNetworkRequest(u)).json()

    def create_entitlement(self, manifest_id: str, type_: str = None):
        """Creates a URL where you can upload a manifest file and notify users
        that they have an entitlement.  Entitlements are digital items that
        users are entitled to use.  Twitch entitlements are granted to users
        gratis or as part of a purchase on Twitch.

        * Requires app access token"""
        if type_ is not None and type_ != 'bulk_drops_grant':
            raise ValueError('Parameter "type_" can only be bulk_drops_grant')

        if type_ is None:
            type_ = 'bulk_drops_grant'

        return self.request(
            'POST',
            'entitlements/upload',
            params=self.validate_query(
                manifest_id=manifest_id,
                type=type_
            )
        )

    def get_code_status(self, code: Union[str, List[str]], user_id: int = None):
        """Gets the status of one or more provided codes.  This API requires
        that the caller is an authenticated Twitch user.  The API is throttled
        to one request per second per authenticated user.

        * Requires an app access token"""
        return self.request(
            'GET',
            'entitlements/codes',
            params=self.validate_query(
                code=code,
                user_id=user_id
            )
        )

    def redeem_code(self, code: Union[str, List[str]], user_id: int = None):
        """The API requires that the caller is an authenticated Twitch user.
        The API is throttled to one request per second per authenticated user.

        * Requires an app access token"""
        return self.request(
            'POST',
            'entitlements/codes',
            params=self.validate_query(
                code=code,
                user_id=user_id
            )
        )

    def get_top_games(self, *, after: str = None, before: str = None, first: int = None):
        """Gets games sorted by number of current viewers on Twitch, most
        popular first.

        Thee response has a JSON payload with a data field containing an array
        of games information elements and a pagination field containing
        information required to query for more streams."""
        if first is not None and first > 100:
            raise ValueError('Parameter "first" cannot be greater than 100.')

        return self.request(
            'GET',
            'games/top',
            params=self.validate_query(
                after=after,
                before=before,
                first=first
            )
        )

    def get_games(self, id_: Union[str, List[str]] = None,
                  name: Union[str, List[str]] = None):
        """Gets game information by game ID or name.

        The response has a JSON payload with a data field containing an array of
        game elements."""
        if id_ is None and name is None:
            raise ValueError('Parameter "id_" and/or "name" must be specified.')

        return self.request(
            'GET',
            'games',
            params=self.validate_query(
                id=id_,
                name=name
            )
        )

    def get_streams(self, *, after: str = None, before: str = None,
                    community_id: Union[str, List[str]] = None, first: int = None,
                    game_id: Union[str, List[str]] = None,
                    language: Union[str, List[str]] = None,
                    user_id: Union[str, List[str]] = None,
                    user_login: Union[str, List[str]] = None):
        """Gets information about active streams.  Streams are returned sorted
        by number of current viewers, in descending order.  Across multiple
        pages of results, there may be duplicate or missing streams, as viewers
        join and leave streams.

        The response has a JSON payload with a data field containing an array
        of stream information elements and a pagination field containing
        information required to query for more streams."""
        if first is not None and first > 100:
            raise ValueError('Parameter "first" cannot be greater than 100.')

        return self.request(
            'GET',
            'streams',
            params=self.validate_query(
                community_id=community_id,
                game_id=game_id,
                language=language,
                user_id=user_id,
                user_login=user_login,
                after=after,
                before=before
            )
        )

    def get_streams_metadata(self, *, after: str = None, before: str = None,
                             community_id: Union[str, List[str]] = None, first: int = None,
                             game_id: Union[str, List[str]] = None,
                             language: Union[str, List[str]] = None,
                             user_id: Union[str, List[str]] = None,
                             user_login: Union[str, List[str]] = None):
        """Gets metadata information about active streams playing Overwatch or
        Hearthstone.  Streams are sorted by number of current viewers, in
        descending order.  Across multiple page of results, there may be
        duplicate or missing streams, as viewers join and leave streams.

        The response has a JSON payload with a data field containing an array
        of stream information elements and a pagination field containing
        information required to query for more streams.

        This endpoint has a global rate limit, across all callers.  The limit
        may change over time, but the response includes informative headers:

        +------------------------------------------+---------+
        |                     Name                 |  Value  |
        +==========================================+=========+
        | Ratelimit-Helixstreamsmetadata-Limit     | integer |
        +------------------------------------------+---------+
        | Ratelimit-Helixstreamsmetadata-Remaining | integer |
        +------------------------------------------+---------+
        """
        if first is not None and first > 100:
            raise ValueError('Parameter "first" cannot be greater than 100.')

        return self.request(
            'GET',
            'streams/metadata',
            params=self.validate_query(
                after=after,
                before=before,
                community_id=community_id,
                first=first,
                game_id=game_id,
                language=language,
                user_login=user_login,
                user_id=user_id
            )
        )

    def create_stream_marker(self, user_id: str, *, description: str = None):
        """Creates a `marker` in the stream of a user specified by a user ID.
        A marker is an arbitrary point in a stream that the broadcaster wants to
        mark;  e.g., to easily return to later.  The marker is created at the
        current timestamp in the live broadcast when the request is processed.
        Markers can be created by the stream owner or editors.  The user
        creating the marker is identified by a Bearer token.

        Markers cannot be created in some cases (an error will occur):

        - If the specified user's stream is not live.
        - If VOD (past broadcast) storage is not enabled for the stream.
        - For premieres (live, first-viewing events that combine uploaded videos
        with live chat).
        - For reruns (subsequent (not live) streaming of any past broadcast,
        including past premieres).

        * Required scope: `user:edit:broadcast`"""
        # Stitch the data body
        d = {'user_id': user_id}

        if description is not None:
            d['description'] = description

        return self.request('POST', 'streams/markers', data=json.dumps(d))

    def get_stream_markers(self, user_id, video_id: str = None, *, after: str = None, before: str = None,
                           first: int = None):
        """Gets a list of `markers` for either a specified user's most recent
        stream or a specified VOD/video (stream), ordered by recency.  A marker
        is an arbitrary point in a stream that the broadcaster wants to mark;
        e.g., to easily return to later.  The only markers are returned are
        those created by the user identified by the Bearer token.

        The response has a JSON payload with a data field containing an array of
        marker information elements and a pagination field containing
        information required to query for more follow information.

        * Required scope: `user:read:broadcast`"""
        if first is not None and first > 100:
            raise ValueError('Parameter "first" cannot be greater than 100.')

        return self.request(
            'GET',
            'streams/markers',
            params=self.validate_query(
                user_id=user_id,
                video_id=video_id,
                after=after,
                before=before,
                first=first
            )
        )

    def get_broadcaster_subscriptions(self, broadcaster_id: str):
        """Gets all of a broadcaster's subscriptions.

        * Required scope: `channel:read:subscriptions`
        * Broadcasters can only request their own subscriptions"""
        return self.request(
            'GET',
            'subscriptions',
            params=self.validate_query(
                broadcaster_id=broadcaster_id
            )
        )

    def get_broadcasters_subscribers(self, broadcaster_id: str, user_id: Union[str, List[str]] = None):
        """Gets broadcaster's subscriptions by user ID (one or more).

        * Required scope: `channel:read:subscriptions`
        * Users can only request their own subscriptions"""
        return self.request(
            'GET',
            'subscriptions',
            params=self.validate_query(
                broadcaster_id=broadcaster_id,
                user_id=user_id
            )
        )

    def get_all_stream_tags(self, *, after: str = None, first: int = None, tag_id: Union[str, List[str]]):
        """Gets the list of all stream tags defined by Twitch, optionally
        filtered by tag ID(s).

        The response has a JSON payload with a data field containing an array
        of tag elements and a pagination field containing information required
        to query for more tags.

        * Requires app access token"""
        if first is not None and first > 100:
            raise ValueError('Parameter "first" cannot be greater than 100.')

        return self.request(
            'GET',
            'tags/streams',
            params=self.validate_query(
                after=after,
                first=first,
                tag_id=tag_id
            )
        )

    def get_stream_tags(self, broadcaster_id: str):
        """Gets a list of tags for a specified stream (channel).

        The response has a JSON payload with a `data` field containing an array
        of tag elements.

        * Requires app access token"""
        return self.request(
            'GET',
            'streams/tags',
            params=self.validate_query(broadcaster_id=broadcaster_id)
        )

    def replace_stream_tags(self, broadcaster_id: str, tag_ids: List[str] = None):
        """Applies specified tags to a specified stream, overwriting any
        existing tags applied to that stream.  If no tags are specified, all
        tags previously applied to the stream are removed.  Automated tags are
        not affected by this operation.

        Tags expire 72 hours after they are applied, unless the stream is live
        within that time period.  If the stream is live within 72-hour window,
        the 72-hour clock restarts when the stream goes offline.  The expiration
        period is subject to change.

        * Required scope: `user:edit:broadcast`"""
        # The API only lets up to 5 tags be applied to a stream,
        # but the API supports up to 100 tag ids.  The 5 tag limit
        # should be enforced upstream.
        if tag_ids is not None and len(tag_ids) > 100:
            raise ValueError('Parameter "tag_ids" cannot contain more than 100 entries.')

        if tag_ids is not None:
            data = json.dumps({'tag_ids': tag_ids})

        else:
            data = None

        return self.request(
            'PUT',
            'streams/tags',
            params=self.validate_query(broadcaster_id=broadcaster_id),
            data=data
        )

    def get_users(self, *, id_: Union[str, List[str]] = None,
                  login: Union[str, List[str]] = None):
        """Gets information about one or more specified Twitch users.  Users
        are identified by optional user IDs and/or login name.  If neither a
        user ID nor a login name is specified, the user is looked up by Bearer
        token.

        The response has a JSON payload with a `data` field containing an array
        of user-information elements.

        * Optional scope: `user:read:email`"""
        if id_ is not None and isinstance(id_, list) and len(id_) > 100:
            raise ValueError('Parameter "id_" cannot contain more than 100 values.')

        if login is not None and isinstance(login, list) and len(login) > 100:
            raise ValueError('Parameter "login" cannot contain more than 100 values.')

        return self.request(
            'GET',
            'users',
            params=self.validate_query(id=id, login=login)
        )

    def get_users_follows(self, *, after: str = None, first: int = None, from_id: str = None, to_id: str = None):
        """Gets information on follow relationships between two Twitch users.
        Information returned is sorted in order, most recent follow first.  This
        can return information like "who is lirik following," "who is following
        lirik," or "is user X following user Y."

        This response has a JSON payload with a data field containing an array
        of follow relationship elements and a pagination field containing
        information required to query for more follow information."""
        if from_id is None and to_id is None:
            raise ValueError('"from_id" and/or "to_id" must be provided.')

        if first is not None and first > 100:
            raise ValueError('Parameter "first" cannot be greater than 100.')

        return self.request(
            'GET',
            'users/follows',
            params=self.validate_query(
                after=after,
                first=first,
                from_id=from_id,
                to_id=to_id
            )
        )

    def update_user(self, description: str):
        """Updates the description of a user specified by a Bearer token.

        * Required scope: `user:edit`"""
        return self.request('PUT', 'users', params={'description': description})

    def get_user_extensions(self):
        """Gets a list of all extensions (both active and inactive) for a
        specified user, identified by a Bearer token.

        The response has JSON payload with a data field containing an array of
        user-information elements.

        * Required scope: `user:read:broadcast`"""
        return self.request('GET', 'users/extensions/list')

    def get_user_active_extensions(self, *, user_id: str = None):
        """Gets information about active extensions installed by a specified
        user, identified by a user ID or Bearer token.

        * Optional scope: `user:read:broadcast` or `user:edit:broadcast`"""
        return self.request('GET', 'users/extensions', params=self.validate_query(user_id=user_id))

    def update_user_extensions(self, panel: List[dict], overlay: List[dict],
                               component: List[dict]):
        """Updates the activation state, extension ID, and/or version number of
        installed extensions for a specified user, identified by a Bearer token.
        If you try to activate a given extension under multiple extension types,
        the last write wins (and there is no guarantee of write order).

        * Required scope: `user:edit:broadcast`"""
        data = {
            'panel': {str(i): d for i, d in enumerate(panel, start=1)},
            'overlay': {str(i): d for i, d in enumerate(overlay, start=1)},
            'component': {str(i): d for i, d in enumerate(component, start=1)}
        }

        return self.request(
            'PUT',
            'users/extensions',
            data=json.dumps(data)
        )

    def get_videos(self, id_: Union[str, List[str]] = None, user_id: str = None, game_id: str = None,
                   after: str = None, before: str = None, first: int = None,
                   language: str = None, period: str = None, sort: str = None, type_: str = None):
        """Gets video information by video ID (one or more), user ID (one only),
        or game ID (one only).

        The response has a JSON payload with a data field containing an array of
        video elements.  For lookup by user or game, pagination is available,
        along with several filters that can be specified as query string
        parameters."""
        if id_ is None and user_id is None and game_id is None:
            raise ValueError('"id_", "user_id", and/or "game_id" must be specified.')

        if first is not None and first > 100:
            raise ValueError('Parameter "first" cannot be greater than 100.')

        if period is not None and period not in ['all', 'day', 'week', 'month']:
            raise ValueError('Parameter "period" can only be all, day, week, or month.')

        if sort is not None and sort not in ['time', 'trending', 'views']:
            raise ValueError('Parameter "sort" can only be time, trending, or views.')

        if type_ is not None and type_ not in ['all', 'upload', 'archive', 'highlight']:
            raise ValueError('Parameter "type_" can only be all, upload, archive, or highlight.')

        return self.request(
            'GET',
            'videos',
            params=self.validate_query(
                id=id_,
                user_id=user_id,
                game_id=game_id,
                after=after,
                before=before,
                first=first,
                language=language,
                period=period,
                sort=sort,
                type=type_
            )
        )

    def get_webhook_subscriptions(self, *, after: str = None, first: int = None):
        """Gets the Webhook subscriptions of user identified by a Bearer token,
        in order of expiration.

        The response has a JSON payload with a data field containing an array of
        subscription elements and a pagination field containing information
        required to query for more subscriptions.

        * Requires app access token"""
        if first is not None and first > 100:
            raise ValueError('Parameter "first" cannot be greater than 100.')

        return self.request(
            'GET',
            'webhooks/subscriptions',
            params=self.validate_query(
                after=after,
                first=first
            )
        )
