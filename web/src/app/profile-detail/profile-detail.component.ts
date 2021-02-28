import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';

import { environment } from 'src/environments/environment';
import { APIService } from '../api.service';
import { Profile } from '../entities';


class ProfileConfiguration {
  display_name = ""
  auto_archive = false
}

@Component({
  selector: 'app-profile-detail',
  templateUrl: './profile-detail.component.html',
  styleUrls: ['./profile-detail.component.scss']
})
export class ProfileDetailComponent implements OnInit {
  profile$: Observable<Profile>;
  configuration = new ProfileConfiguration()
  username?: string;

  constructor(private route: ActivatedRoute, private router: Router, private apiService: APIService) {
    this.profile$ = this.route.paramMap.pipe(
      switchMap(params => {
        return this.apiService.getProfile(params.get("username") ?? "")
      })
    );
    this.profile$.subscribe( profile => {
      this.configuration.display_name = profile.display_name
      this.configuration.auto_archive = profile.auto_archive
    })
  }

  ngOnInit(): void { }

  profileImagePath(filename: string): string {
    return `${environment.apiRoot}/media/profile_images/${filename}`
  }

  saveConfiguration() {

  }
}
